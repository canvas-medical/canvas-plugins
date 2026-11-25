"""What reaches Sentry from an agent run's or a handler's exception."""

import json
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any, cast
from unittest.mock import MagicMock

import pytest
import sentry_sdk
from sentry_sdk.envelope import Envelope
from sentry_sdk.transport import Transport

from canvas_sdk.effects import Effect
from canvas_sdk.effects.simple_api import DenyConnection, Response
from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.handlers.simple_api import SimpleAPIRoute
from canvas_sdk.handlers.simple_api.security import Credentials
from canvas_sdk.handlers.simple_api.websocket import WebSocketAPI
from canvas_sdk.tests.handlers.simple_api.test_api import handle_request
from canvas_sdk.tests.handlers.simple_api.test_websocket import make_auth_event
from canvas_sdk.tests.utils.test_http import (
    _certificate_pem,
    _key_pem,
    _private_key,
    _signed_certificate,
)
from canvas_sdk.utils import Http
from plugin_runner.plugin_runner import (
    LOADED_PLUGINS,
    PluginRunner,
    _report_agent_exception,
    reconcile_plugins,
    reload_plugin,
)

CHART_TEXT = "Jane Doe, A1c 9.1"

CA_KEY = _private_key()
CLIENT_KEY = _private_key()
CLIENT_CERT = _certificate_pem(_signed_certificate("plugin-client", CLIENT_KEY, "test-ca", CA_KEY))
CLIENT_KEY_PEM = _key_pem(CLIENT_KEY)
UNRELATED_KEY_PEM = _key_pem(_private_key())


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
    """Sentry with events kept here, sending default PII as the runner's settings do.

    Each test runs in its own isolation scope, so a breadcrumb one test records is not
    in the next test's events.
    """
    _Captured.events = []
    sentry_sdk.init(
        dsn="https://key@sentry.invalid/1",
        transport=_Captured,
        send_default_pii=True,
        include_local_variables=True,
    )
    try:
        with sentry_sdk.isolation_scope():
            yield _Captured.events
    finally:
        sentry_sdk.init()


def _raise_with_chart_text() -> None:
    conversation = [{"role": "user", "content": CHART_TEXT}]
    raise KeyError(conversation[0]["content"])


def test_an_agent_runs_exception_reaches_sentry_with_neither_locals_nor_message(
    sentry_events: list[dict[str, Any]],
) -> None:
    """The message can carry chart text, so the type and run id stand in for it.

    The runner publishes each log line to Redis, and Sentry's Redis integration records the
    publish, traceback included, as a breadcrumb; this one stands in for it, so the test
    holds wherever Redis is reachable or not.
    """
    sentry_sdk.add_breadcrumb(
        category="redis", message=f"PUBLISH plugin-logging-stream KeyError: '{CHART_TEXT}'"
    )
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


def test_an_agent_runs_log_breadcrumb_does_not_reach_a_later_event(
    sentry_events: list[dict[str, Any]], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Breadcrumbs outlive the event they were recorded beside, so the publish of an agent
    run's traceback must not stay behind for the next error the process reports.
    """

    def publish(message: str, *args: Any, **kwargs: Any) -> None:
        # What the runner's log handler does: publish the line, which Sentry records.
        sentry_sdk.add_breadcrumb(category="redis", message=f"PUBLISH KeyError: '{CHART_TEXT}'")

    monkeypatch.setattr("plugin_runner.plugin_runner.log.exception", publish)
    try:
        _raise_with_chart_text()
    except KeyError as exc:
        _report_agent_exception("RunAgent: agent a raised", exc, "run-1")
    sentry_sdk.capture_message("a handler failed later")
    sentry_sdk.flush()

    assert len(sentry_events) == 2
    assert CHART_TEXT not in json.dumps(sentry_events)


def test_a_mismatched_client_key_never_reaches_sentry_from_a_simple_api_route(
    sentry_events: list[dict[str, Any]],
) -> None:
    """``load_cert_chain`` refuses the key inside ``Http.__init__``, whose frame holds it."""

    class Route(SimpleAPIRoute):
        PATH = "/route"

        def authenticate(self, credentials: Credentials) -> bool:
            return True

        def get(self) -> list[Response | Effect]:
            Http("https://bamboo.example", client_cert=CLIENT_CERT, client_key=UNRELATED_KEY_PEM)
            return []

    effects = handle_request(Route, method="GET", path="/route")
    sentry_sdk.flush()

    assert json.loads(effects[0].payload)["status_code"] == 500
    assert sentry_events
    assert "PRIVATE KEY" not in json.dumps(sentry_events), "the private key reached Sentry"


def test_a_failed_request_never_sends_the_client_key_to_sentry_from_a_simple_api_route(
    sentry_events: list[dict[str, Any]],
) -> None:
    """The route's own frame holds the PEMs it passed to ``Http``."""

    class Route(SimpleAPIRoute):
        PATH = "/route"

        def authenticate(self, credentials: Credentials) -> bool:
            return True

        def get(self) -> list[Response | Effect]:
            certificate = (CLIENT_CERT, CLIENT_KEY_PEM)
            Http("https://127.0.0.1:1", client_cert=certificate[0], client_key=certificate[1]).get(
                "/report"
            )
            return []

    effects = handle_request(Route, method="GET", path="/route")
    sentry_sdk.flush()

    assert json.loads(effects[0].payload)["status_code"] == 500
    assert sentry_events
    assert "PRIVATE KEY" not in json.dumps(sentry_events), "the private key reached Sentry"


def test_a_mismatched_client_key_never_reaches_sentry_from_a_websocket_authenticate(
    sentry_events: list[dict[str, Any]],
) -> None:
    """A WebSocket handler reports its exception the way a SimpleAPI route does."""

    class Socket(WebSocketAPI):
        def authenticate(self) -> bool:
            Http("https://bamboo.example", client_cert=CLIENT_CERT, client_key=UNRELATED_KEY_PEM)
            return True

    effects = Socket(event=make_auth_event(channel="channel")).compute()
    sentry_sdk.flush()

    assert effects == [DenyConnection(message="Internal server error").apply()]
    assert sentry_events
    assert "PRIVATE KEY" not in json.dumps(sentry_events), "the private key reached Sentry"


def test_an_unknown_event_type_reaches_sentry_without_the_events_context(
    sentry_events: list[dict[str, Any]], monkeypatch: pytest.MonkeyPatch
) -> None:
    """``Event.__init__`` holds the request and its parsed context when the name lookup fails."""
    monkeypatch.setattr("settings.IS_TESTING", False)

    unknown_type = cast(EventType, 99999)
    event = Event(EventRequest(type=unknown_type, context=json.dumps({"note": CHART_TEXT})))
    sentry_sdk.flush()

    assert event.name == "UNKNOWN_EVENT_99999"
    assert sentry_events
    assert CHART_TEXT not in json.dumps(sentry_events)


def _plugin_with_secrets(
    root: Path, manifest: dict[str, Any], secrets_text: str, name: str = "pdmp_probe"
) -> Path:
    plugin = root / name
    plugin.mkdir()
    (plugin / "CANVAS_MANIFEST.json").write_text(json.dumps({"name": name, **manifest}))
    (plugin / "SECRETS.json").write_text(secrets_text)
    return plugin


def _load_by_reload(plugin: Path) -> None:
    reload_plugin(plugin)


def _load_by_reconcile(plugin: Path) -> None:
    reconcile_plugins([plugin.as_posix()])


@pytest.mark.parametrize("load", [_load_by_reload, _load_by_reconcile])
def test_a_namespace_access_error_never_sends_the_plugins_secrets_to_sentry(
    tmp_path: Path,
    sentry_events: list[dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
    load: Callable[[Path], None],
) -> None:
    """A plugin installed before its namespace key is set fails to load with its secrets loaded."""
    monkeypatch.setattr("plugin_runner.plugin_runner.IS_SQLITE", False)
    plugin = _plugin_with_secrets(
        tmp_path,
        {
            "components": {"handlers": []},
            "custom_data": {"namespace": "acme__pdmp", "access": "read"},
        },
        json.dumps({"client_cert": "cert", "client_key": CLIENT_KEY_PEM}),
    )

    load(plugin)
    sentry_sdk.flush()

    assert sentry_events
    assert "PRIVATE KEY" not in json.dumps(sentry_events), "the plugin's secrets reached Sentry"


def test_a_failed_namespace_key_check_never_sends_the_access_key_to_sentry(
    tmp_path: Path,
    sentry_events: list[dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """verify_plugin_namespace_access holds the key when the auth table lookup raises."""
    monkeypatch.setattr("plugin_runner.plugin_runner.IS_SQLITE", False)

    def unreachable(namespace: str, key: str) -> str:
        raise RuntimeError("namespace auth table unreachable")

    monkeypatch.setattr("plugin_runner.namespace.check_namespace_auth_key", unreachable)
    plugin = _plugin_with_secrets(
        tmp_path,
        {
            "components": {"handlers": []},
            "custom_data": {"namespace": "acme__pdmp", "access": "read"},
        },
        json.dumps({"namespace_read_access_key": CLIENT_KEY_PEM}),
    )

    reload_plugin(plugin)
    sentry_sdk.flush()

    assert sentry_events
    assert "PRIVATE KEY" not in json.dumps(sentry_events), "the access key reached Sentry"


@pytest.mark.parametrize(
    "manifest,secrets_text",
    [
        pytest.param(
            {"components": {"handlers": []}},
            '{"client_key": ' + json.dumps(CLIENT_KEY_PEM),
            id="malformed SECRETS.json",
        ),
        pytest.param(
            {},
            json.dumps({"client_key": CLIENT_KEY_PEM}),
            id="manifest without components",
        ),
    ],
)
def test_a_plugin_that_fails_to_load_never_sends_its_secrets_to_sentry(
    tmp_path: Path,
    sentry_events: list[dict[str, Any]],
    manifest: dict[str, Any],
    secrets_text: str,
) -> None:
    """import_plugin's own reports come from frames that hold the secrets or their file's text."""
    plugin = _plugin_with_secrets(tmp_path, manifest, secrets_text)

    reload_plugin(plugin)
    sentry_sdk.flush()

    assert sentry_events
    assert "PRIVATE KEY" not in json.dumps(sentry_events), "the plugin's secrets reached Sentry"
