"""What reaches Sentry from an agent run's or a handler's exception."""

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
import sentry_sdk
from sentry_sdk.envelope import Envelope
from sentry_sdk.transport import Transport

from canvas_sdk.events import EventRequest, EventType
from plugin_runner.plugin_runner import LOADED_PLUGINS, PluginRunner, _report_agent_exception

CHART_TEXT = "Jane Doe, A1c 9.1"


class _Captured(Transport):
    events: list[dict[str, Any]] = []

    def capture_envelope(self, envelope: Envelope) -> None:
        event = envelope.get_event()
        if event is not None:
            self.events.append(dict(event))


@pytest.fixture
def plugin_runner() -> PluginRunner:
    """A runner with its metrics client stubbed."""
    runner = PluginRunner()
    runner.statsd_client = MagicMock()  # type: ignore[attr-defined]
    return runner


@pytest.fixture
def sentry_events() -> Iterator[list[dict[str, Any]]]:
    """Sentry with events kept here, sending default PII as the runner's settings do."""
    _Captured.events = []
    sentry_sdk.init(
        dsn="https://key@sentry.invalid/1",
        transport=_Captured,
        send_default_pii=True,
        include_local_variables=True,
    )
    try:
        yield _Captured.events
    finally:
        sentry_sdk.init()


def _raise_with_chart_text() -> None:
    conversation = [{"role": "user", "content": CHART_TEXT}]
    raise KeyError(conversation[0]["content"])


def test_an_agent_runs_exception_reaches_sentry_with_neither_locals_nor_message(
    sentry_events: list[dict[str, Any]],
) -> None:
    """The message can carry chart text, so the type and run id stand in for it."""
    try:
        _raise_with_chart_text()
    except KeyError as exc:
        _report_agent_exception("RunAgent: agent a raised", exc, "run-1")
    sentry_sdk.flush()

    assert sentry_events
    sent = json.dumps(sentry_events)
    assert CHART_TEXT not in sent
    values = [v for event in sentry_events for v in event.get("exception", {}).get("values", [])]
    assert values and all(v["value"] == "KeyError in agent run run-1" for v in values)


@pytest.mark.parametrize("install_test_plugin", ["example_plugin"], indirect=True)
def test_a_handlers_exception_reaches_sentry_without_frame_locals(
    install_test_plugin: Path,
    plugin_runner: PluginRunner,
    load_test_plugins: None,
    db: None,
    sentry_events: list[dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A handler's frames hold the event's context, such as a SimpleAPI request's body."""

    def compute(self: Any) -> list[Any]:
        request_body = CHART_TEXT  # noqa: F841 - a local Sentry would otherwise send
        raise RuntimeError("handler failed")

    for entry in LOADED_PLUGINS.values():
        monkeypatch.setattr(entry["class"], "compute", compute)

    list(plugin_runner.HandleEvent(EventRequest(type=EventType.UNKNOWN), None))
    sentry_sdk.flush()

    assert sentry_events
    frames = [
        frame
        for event in sentry_events
        for value in event.get("exception", {}).get("values", [])
        for frame in value.get("stacktrace", {}).get("frames", [])
    ]
    assert frames and not any("vars" in frame for frame in frames)
    assert CHART_TEXT not in json.dumps(sentry_events)
