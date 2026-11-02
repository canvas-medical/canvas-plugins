import json
import threading
import time
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import anthropic
import httpx2
import pytest

import plugin_runner.plugin_runner as runner_module
from canvas_generated.messages.effects_pb2 import EffectType
from canvas_generated.messages.plugins_pb2 import (
    RunAgentRequest,
    RunAgentRequester,
    RunAgentSubject,
)
from canvas_sdk.agents import AgentRunResult, ToolRegistry
from canvas_sdk.agents.run_record import (
    DEADLINE_MARGIN_SECONDS,
    RUN_TOOL_RESULT_CHARS,
    RunDeadlineExceeded,
    ToolCallRecord,
    current_recorder,
)
from canvas_sdk.effects import Effect
from canvas_sdk.effects.agent import RunAgentEffect
from canvas_sdk.effects.banner_alert.add_banner_alert import AddBannerAlert
from canvas_sdk.effects.task.task import AddTask
from plugin_runner.plugin_runner import (
    EVENT_HANDLER_MAP,
    LOADED_PLUGINS,
    PluginRunner,
)
from settings import extended_agent_run_limit

AGENT_KEY = "test_agent_plugin:test_agent_plugin.agents.echo_agent:EchoAgent"
AGENT_ID = "test_agent_plugin.agents.echo_agent:EchoAgent"


@pytest.fixture
def plugin_runner() -> PluginRunner:
    """Construct a PluginRunner with statsd mocked out for unit tests."""
    runner = PluginRunner()
    runner.statsd_client = MagicMock()  # type: ignore[attr-defined]
    return runner


@pytest.fixture
def inference_gateway_env(load_test_plugins: None, monkeypatch: pytest.MonkeyPatch) -> None:
    """Configure the inference gateway the way an instance and an agent plugin do.

    The gateway URL is instance config; the key is the agent plugin's own
    INFERENCE_GATEWAY_KEY secret.
    """
    monkeypatch.setenv("INFERENCE_GATEWAY_URL", "https://gateway.test")
    LOADED_PLUGINS[AGENT_KEY]["secrets"] = {"INFERENCE_GATEWAY_KEY": "cnvs_sk_test_plugin"}


def _make_request(
    *,
    agent_id: str = AGENT_ID,
    scope_key: str = "patient:p1",
    trigger_payload: str = '{"message": "hi"}',
    plugin_name: str = "test_agent_plugin",
    handler_name: str = "EchoTrigger",
    actor: str = "1",
    source: str = "handler",
    stream_progress: bool = False,
) -> RunAgentRequest:
    return RunAgentRequest(
        stream_progress=stream_progress,
        agent_id=agent_id,
        scope_key=scope_key,
        run_id="run-1",
        trigger_payload=trigger_payload,
        plugin_name=plugin_name,
        handler_name=handler_name,
        requester=RunAgentRequester(actor=actor, source=source, staff_id="s1"),
        subject=RunAgentSubject(patient_id="p1", note_id="n1"),
    )


# Loader changes ----------------------------------------------------------------


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_components_agents_load_into_loaded_plugins(
    install_test_plugin: Path, load_test_plugins: None
) -> None:
    """Agent classes declared under components.agents[] register in LOADED_PLUGINS."""
    assert AGENT_KEY in LOADED_PLUGINS
    assert LOADED_PLUGINS[AGENT_KEY]["active"] is True


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_agents_do_not_appear_in_event_handler_map(
    install_test_plugin: Path, load_test_plugins: None
) -> None:
    """AgentPlugin subclasses have no RESPONDS_TO, so they must not subscribe to events."""
    for handlers in EVENT_HANDLER_MAP.values():
        assert AGENT_KEY not in handlers, (
            f"agent {AGENT_KEY} should not be registered for any event"
        )


# RunAgent happy path -----------------------------------------------------------


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_happy_path_returns_emitted_effect(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
) -> None:
    """A valid RunAgent invocation produces success=True and the agent's emitted effect."""
    responses = list(plugin_runner.RunAgent(_make_request(), None))

    assert len(responses) == 1
    response = responses[0]
    assert response.success is True
    assert len(response.effects) == 1

    effect = response.effects[0]
    assert effect.type == EffectType.LOG

    body = json.loads(effect.payload)
    assert body == {
        "loaded_with": "patient:p1",
        "trigger": {"message": "hi"},
        "subject": ["p1", "s1", "n1", None, []],
        "run_id": "run-1",
        "gateway_model": "claude-sonnet-4-6",
    }


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_leaves_absent_subject_fields_unset(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
) -> None:
    """A run with no requester, such as one a system event started, has no staff_id."""
    request = _make_request()
    request.requester.staff_id = ""

    (response,) = plugin_runner.RunAgent(request, None)

    assert json.loads(response.effects[0].payload)["subject"] == ["p1", None, "n1", None, []]


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_sets_the_claim_and_capabilities_from_the_request(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
) -> None:
    """The claim and the capabilities the platform granted reach the agent.

    A capability this SDK does not know is left out rather than failing the run.
    """
    request = _make_request()
    request.subject.claim_id = "c1"
    request.capabilities.extend(["revenue", "from_a_newer_platform"])

    (response,) = plugin_runner.RunAgent(request, None)

    assert json.loads(response.effects[0].payload)["subject"] == [
        "p1",
        "s1",
        "n1",
        "c1",
        ["revenue"],
    ]


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_stamps_provenance_on_emitted_effects(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
) -> None:
    """Emitted effects carry plugin_name, handler_name, actor, source.

    ``handler_name`` is the agent class rather than the trigger handler that
    emitted the RunAgentEffect, so the security audit names the agent behind
    each write. ``classname`` is intentionally left empty on agent-emitted effects
    (see plugin_runner.py:RunAgent for the rationale): the home-app
    interpreters treat a populated classname as a CQM Protocol identifier
    and would route agent effects through the wrong code path.
    """
    request = _make_request(
        plugin_name="test_agent_plugin",
        handler_name="EchoTrigger",
        actor="42",
        source="handler",
    )
    response = next(iter(plugin_runner.RunAgent(request, None)))

    effect = response.effects[0]
    assert effect.plugin_name == "test_agent_plugin"
    assert effect.classname == ""
    assert effect.handler_name == "EchoAgent"
    assert effect.actor == "42"
    assert effect.source == "handler"


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_defaults_source_to_agent_when_request_omits_it(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
) -> None:
    """Effects emitted by the agent default source to "agent" when the caller didn't set it."""
    response = next(iter(plugin_runner.RunAgent(_make_request(source=""), None)))
    assert response.effects[0].source == "agent"


# RunAgent error paths ----------------------------------------------------------


def test_run_agent_invalid_agent_id_format(plugin_runner: PluginRunner) -> None:
    """An agent_id missing the ':' separator is rejected before any plugin lookup."""
    response = next(iter(plugin_runner.RunAgent(_make_request(agent_id="no_colon_here"), None)))
    assert response.success is False
    assert list(response.effects) == []


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_unknown_agent_id(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
) -> None:
    """A well-formed agent_id that isn't in LOADED_PLUGINS yields success=False."""
    request = _make_request(agent_id="test_agent_plugin.agents.echo_agent:NoSuchClass")
    response = next(iter(plugin_runner.RunAgent(request, None)))
    assert response.success is False
    assert list(response.effects) == []


@pytest.mark.parametrize("plugin_name", ["another_plugin", ""], ids=["other", "blank"])
@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_refuses_an_agent_the_requesting_plugin_does_not_own(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
    monkeypatch: pytest.MonkeyPatch,
    plugin_name: str,
) -> None:
    """Only the plugin that ships an agent can run it, with its key, data, and tool grants."""
    agent_cls = LOADED_PLUGINS[AGENT_KEY]["class"]
    ran: list[bool] = []
    monkeypatch.setattr(agent_cls, "load_state", lambda self, scope_key: ran.append(True))

    response = next(iter(plugin_runner.RunAgent(_make_request(plugin_name=plugin_name), None)))

    assert response.success is False
    assert list(response.effects) == []
    assert ran == []


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_drops_usage_the_plugin_is_not_priced_in(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Agent effects pass the same RecordUsage gate handler effects do.

    The grant includes a tool declaring RECORD_USAGE, so the usage gate is the only
    thing that can drop the record.
    """
    agent_cls = LOADED_PLUGINS[AGENT_KEY]["class"]
    monkeypatch.setitem(
        LOADED_PLUGINS[AGENT_KEY]["handler"], "tools", {"allowed": ["echo", "meter"]}
    )
    usage = Effect(
        type=EffectType.RECORD_USAGE,
        payload=json.dumps({"data": {"unit": "unpriced unit", "key": "k", "quantity": 999}}),
    )
    log_effect = Effect(type=EffectType.LOG, payload="{}")
    monkeypatch.setattr(
        agent_cls,
        "run",
        lambda self, state, gateway, payload: AgentRunResult(state, [usage, log_effect]),
    )

    response = next(iter(plugin_runner.RunAgent(_make_request(), None)))

    assert response.success is True
    assert [effect.type for effect in response.effects] == [EffectType.LOG]
    assert response.agent_run.effects_dropped == 1

    monkeypatch.setitem(LOADED_PLUGINS[AGENT_KEY], "usage_units", frozenset({"unpriced unit"}))
    priced = next(iter(plugin_runner.RunAgent(_make_request(), None)))

    assert [effect.type for effect in priced.effects] == [EffectType.RECORD_USAGE, EffectType.LOG]


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_without_gateway_configuration_short_circuits(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Without the gateway URL or the plugin's key, the RPC refuses to dispatch and says why."""
    monkeypatch.delenv("INFERENCE_GATEWAY_URL", raising=False)
    LOADED_PLUGINS[AGENT_KEY]["secrets"] = {}
    response = next(iter(plugin_runner.RunAgent(_make_request(), None)))
    assert response.success is False
    assert list(response.effects) == []
    assert response.error_kind == "LLM_NOT_CONFIGURED"


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_needs_the_plugins_gateway_key(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A gateway URL alone is not enough; the plugin needs its own INFERENCE_GATEWAY_KEY."""
    monkeypatch.setenv("INFERENCE_GATEWAY_URL", "https://gateway.test")
    LOADED_PLUGINS[AGENT_KEY]["secrets"] = {"ANTHROPIC_API_KEY": "sk-ant-plugin"}
    response = next(iter(plugin_runner.RunAgent(_make_request(), None)))
    assert response.error_kind == "LLM_NOT_CONFIGURED"


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_attributes_the_gateway_to_the_plugin_agent_and_run(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The runner builds the gateway from the plugin's key and attributes it to the run."""
    agent_cls = LOADED_PLUGINS[AGENT_KEY]["class"]
    seen: list[Any] = []
    original_run = agent_cls.run

    def _capture(self, state, gateway, trigger_payload):  # type: ignore[no-untyped-def]
        seen.append(gateway)
        return original_run(self, state, gateway, trigger_payload)

    monkeypatch.setattr(agent_cls, "run", _capture)
    response = next(iter(plugin_runner.RunAgent(_make_request(), None)))

    assert response.success is True
    assert seen[0].api_key == "cnvs_sk_test_plugin"
    assert seen[0].base_url == "https://gateway.test"
    attribution = seen[0].attribution
    assert attribution["plugin"] == "test_agent_plugin"
    assert attribution["agent"] == AGENT_ID
    assert attribution["run-id"] == "run-1"
    assert attribution["instance"]


def _status_error(status: int) -> Exception:
    request = httpx2.Request("POST", "https://gateway.test/v1/messages")
    response = httpx2.Response(status, request=request, json={"error": {"message": "no"}})
    return anthropic.APIStatusError("no", response=response, body=None)


def _connection_error() -> Exception:
    return anthropic.APIConnectionError(
        request=httpx2.Request("POST", "https://gateway.test/v1/messages")
    )


@pytest.mark.parametrize(
    "make_error, error_kind",
    [
        (lambda: _status_error(402), "LLM_REFUSED"),
        (lambda: _status_error(404), "LLM_REFUSED"),
        (lambda: _status_error(400), "LLM_REFUSED"),
        (lambda: _status_error(401), "LLM_REFUSED"),
        (lambda: _status_error(429), "LLM_UNAVAILABLE"),
        (lambda: _status_error(502), "LLM_UNAVAILABLE"),
        (_connection_error, "LLM_UNAVAILABLE"),
    ],
    ids=["402", "404", "400", "401", "429", "502", "connection"],
)
@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_tags_gateway_failures_by_whether_a_retry_could_help(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
    monkeypatch: pytest.MonkeyPatch,
    make_error: Any,
    error_kind: str,
) -> None:
    """Outages are LLM_UNAVAILABLE; anything a retry would hit again is LLM_REFUSED."""
    agent_cls = LOADED_PLUGINS[AGENT_KEY]["class"]

    def _fail(self, state, gateway, trigger_payload):  # type: ignore[no-untyped-def]
        raise make_error()

    monkeypatch.setattr(agent_cls, "run", _fail)
    response = next(iter(plugin_runner.RunAgent(_make_request(), None)))
    assert response.success is False
    assert response.error_kind == error_kind


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_invalid_trigger_payload_json(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
) -> None:
    """Malformed trigger_payload JSON is reported instead of crashing the worker."""
    request = _make_request(trigger_payload="not-json{{{")
    response = next(iter(plugin_runner.RunAgent(request, None)))
    assert response.success is False
    assert list(response.effects) == []


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_handles_agent_exceptions(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exceptions raised by the agent's run() surface as success=False."""
    agent_cls = LOADED_PLUGINS[AGENT_KEY]["class"]

    def _boom(self, state, gateway, trigger_payload):  # type: ignore[no-untyped-def]
        raise RuntimeError("agent kaboom")

    monkeypatch.setattr(agent_cls, "run", _boom)
    response = next(iter(plugin_runner.RunAgent(_make_request(), None)))
    assert response.success is False
    assert list(response.effects) == []


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_does_not_set_error_kind_on_generic_failure(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A generic exception inside the agent leaves error_kind empty.

    error_kind is reserved for *expected* failure modes the caller should
    react to specifically (the LLM_* kinds). Unstructured exceptions still
    surface as success=False, but error_kind must stay empty so the caller
    doesn't mistake them for a retryable gateway outage.
    """
    agent_cls = LOADED_PLUGINS[AGENT_KEY]["class"]

    def _boom(self, state, gateway, trigger_payload):  # type: ignore[no-untyped-def]
        raise RuntimeError("agent code bug")

    monkeypatch.setattr(agent_cls, "run", _boom)
    response = next(iter(plugin_runner.RunAgent(_make_request(), None)))
    assert response.success is False
    assert response.error_kind == ""


# ---------------------------------------------------------------------------
# Lifecycle hooks (on_run_start / on_run_end / on_run_error)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_fires_on_run_start_and_on_run_end_in_order(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Successful runs invoke on_run_start then on_run_end (no on_run_error)."""
    agent_cls = LOADED_PLUGINS[AGENT_KEY]["class"]
    call_log: list[tuple[str, Any]] = []

    monkeypatch.setattr(
        agent_cls,
        "on_run_start",
        lambda self, scope_key: call_log.append(("on_run_start", scope_key)),
    )
    monkeypatch.setattr(
        agent_cls,
        "on_run_end",
        lambda self, result: call_log.append(("on_run_end", result)),
    )
    monkeypatch.setattr(
        agent_cls,
        "on_run_error",
        lambda self, exc: call_log.append(("on_run_error", exc)),
    )

    response = next(iter(plugin_runner.RunAgent(_make_request(), None)))
    assert response.success is True

    assert [name for name, _ in call_log] == ["on_run_start", "on_run_end"]
    assert call_log[0][1] == "patient:p1"
    assert isinstance(call_log[1][1], AgentRunResult)


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_fires_on_run_error_when_run_raises(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An exception in ``run`` triggers on_run_error and skips on_run_end."""
    agent_cls = LOADED_PLUGINS[AGENT_KEY]["class"]
    call_log: list[tuple[str, Any]] = []

    monkeypatch.setattr(
        agent_cls,
        "on_run_start",
        lambda self, scope_key: call_log.append(("on_run_start", scope_key)),
    )
    monkeypatch.setattr(
        agent_cls,
        "on_run_end",
        lambda self, result: call_log.append(("on_run_end", result)),
    )
    monkeypatch.setattr(
        agent_cls,
        "on_run_error",
        lambda self, exc: call_log.append(("on_run_error", type(exc).__name__)),
    )

    def _boom(self, state, gateway, trigger_payload):  # type: ignore[no-untyped-def]
        raise RuntimeError("agent code bug")

    monkeypatch.setattr(agent_cls, "run", _boom)

    response = next(iter(plugin_runner.RunAgent(_make_request(), None)))
    assert response.success is False

    names = [name for name, _ in call_log]
    assert names == ["on_run_start", "on_run_error"], (
        f"on_run_end must NOT fire on failure; got {names}"
    )
    assert call_log[1][1] == "RuntimeError"


# ---------------------------------------------------------------------------
# tools_allowed injection from the manifest
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_sets_tools_allowed_from_manifest(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``components.agents[].tools.allowed`` lands on the agent as a frozenset."""
    # Splice tools.allowed into the loaded manifest entry. Real plugins
    # declare this statically in CANVAS_MANIFEST.json; we mutate at runtime
    # so the test doesn't need its own fixture plugin.
    LOADED_PLUGINS[AGENT_KEY]["handler"]["tools"] = {"allowed": ["echo", "not_registered"]}

    agent_cls = LOADED_PLUGINS[AGENT_KEY]["class"]
    captured: dict[str, Any] = {}

    def _capture(self, state, gateway, trigger_payload):  # type: ignore[no-untyped-def]
        captured["tools_allowed"] = self.tools_allowed
        return AgentRunResult(state=state, effects=[])

    monkeypatch.setattr(agent_cls, "run", _capture)
    next(iter(plugin_runner.RunAgent(_make_request(), None)))

    assert captured["tools_allowed"] == frozenset({"echo"})


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
@pytest.mark.parametrize(
    ("permissions", "all_permissions", "offered"),
    [
        (["api.view_task"], False, {"echo"}),
        (["api.change_task"], False, {"echo", "close_task"}),
        ([], True, {"echo", "close_task"}),
    ],
    ids=["lacks-the-permission", "holds-the-permission", "not-limited"],
)
def test_run_agent_hides_tools_the_requester_cannot_use(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
    monkeypatch: pytest.MonkeyPatch,
    permissions: list[str],
    all_permissions: bool,
    offered: set[str],
) -> None:
    """The requester's permissions from home-app reach the agent and narrow its granted tools."""
    LOADED_PLUGINS[AGENT_KEY]["handler"]["tools"] = {"allowed": ["echo", "close_task"]}
    agent_cls = LOADED_PLUGINS[AGENT_KEY]["class"]
    captured: dict[str, Any] = {}

    def _capture(self, state, gateway, trigger_payload):  # type: ignore[no-untyped-def]
        captured["tools_allowed"] = self.tools_allowed
        captured["permissions"] = self.requester.permissions
        return AgentRunResult(state=state, effects=[])

    monkeypatch.setattr(agent_cls, "run", _capture)
    request = _make_request()
    request.requester.permissions.extend(permissions)
    request.requester.all_permissions = all_permissions

    next(iter(plugin_runner.RunAgent(request, None)))

    assert captured["tools_allowed"] == frozenset(offered)
    assert captured["permissions"] == (None if all_permissions else frozenset(permissions))


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_scopes_agent_tools_to_manifest_allowlist(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Platform substitutes a scoped registry on the agent before run() fires.

    The agent's `self.tools` is the manifest-scoped view, not the full
    registry the class was declared with. Disallowed tools are dropped
    entirely (their executors aren't reachable from the scoped registry).
    """
    # Equip the test agent with a fake tool registry containing three tools.
    full_registry = ToolRegistry()
    for tool_name in ("read_chart", "write_task", "send_message"):
        full_registry.register(
            {"name": tool_name, "description": tool_name, "input_schema": {"type": "object"}},
            lambda arguments, *, ctx: {"name": "irrelevant"},
        )

    agent_cls = LOADED_PLUGINS[AGENT_KEY]["class"]
    monkeypatch.setattr(agent_cls, "tools", full_registry, raising=False)
    LOADED_PLUGINS[AGENT_KEY]["handler"]["tools"] = {"allowed": ["read_chart", "write_task"]}

    captured: dict[str, Any] = {}

    def _capture(self, state, gateway, trigger_payload):  # type: ignore[no-untyped-def]
        captured["tool_names"] = sorted(d["name"] for d in self.tools.definitions())
        # The scoped registry is a distinct object from the source.
        captured["is_distinct_object"] = self.tools is not full_registry
        # The source is unchanged.
        captured["source_unchanged"] = sorted(d["name"] for d in full_registry.definitions())
        return AgentRunResult(state=state, effects=[])

    monkeypatch.setattr(agent_cls, "run", _capture)
    next(iter(plugin_runner.RunAgent(_make_request(), None)))

    assert captured["tool_names"] == ["read_chart", "write_task"]
    assert captured["is_distinct_object"] is True
    assert captured["source_unchanged"] == ["read_chart", "send_message", "write_task"]


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_grants_no_tools_when_manifest_omits_them(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """No manifest declaration → the agent sees no tools and may return no effects."""
    LOADED_PLUGINS[AGENT_KEY]["handler"].pop("tools", None)

    agent_cls = LOADED_PLUGINS[AGENT_KEY]["class"]
    captured: dict[str, Any] = {}
    original_run = agent_cls.run

    def _capture(self, state, gateway, trigger_payload):  # type: ignore[no-untyped-def]
        captured["tools_allowed"] = self.tools_allowed
        captured["tool_names"] = [d["name"] for d in self.tools.definitions()]
        return original_run(self, state, gateway, trigger_payload)

    monkeypatch.setattr(agent_cls, "run", _capture)
    response = next(iter(plugin_runner.RunAgent(_make_request(), None)))

    assert captured["tools_allowed"] == frozenset()
    assert captured["tool_names"] == []
    assert response.success is True
    assert list(response.effects) == []


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_a_reloaded_plugins_narrower_grant_applies_at_once(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
) -> None:
    """An update that takes a tool away must not leave the old, wider grant in force."""
    manifest_path = install_test_plugin / "CANVAS_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["components"]["agents"][0]["tools"]["allowed"] = []
    manifest_path.write_text(json.dumps(manifest))

    runner_module.reload_plugin(install_test_plugin)
    LOADED_PLUGINS[AGENT_KEY]["secrets"] = {"INFERENCE_GATEWAY_KEY": "cnvs_sk_test_plugin"}
    response = next(iter(plugin_runner.RunAgent(_make_request(), None)))

    assert response.success is True
    assert list(response.effects) == []
    assert response.agent_run.effects_dropped == 1


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_drops_effects_no_granted_tool_declares(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An agent returns only effect types its granted tools can stage.

    The fixture grants `echo` (LOG). A task, a banner, and a nested RunAgentEffect
    built directly in agent code are dropped.
    """
    agent_cls = LOADED_PLUGINS[AGENT_KEY]["class"]
    returned = [
        Effect(type=EffectType.LOG, payload="{}"),
        AddTask(title="Call patient", patient_id="p1").apply(),
        AddBannerAlert(
            patient_id="p1",
            key="k",
            narrative="n",
            placement=[AddBannerAlert.Placement.CHART],
            intent=AddBannerAlert.Intent.INFO,
        ).apply(),
        RunAgentEffect(agent_id=AGENT_ID, scope=RunAgentEffect.Scope.AGENT).apply(),
    ]
    monkeypatch.setattr(
        agent_cls, "run", lambda self, state, gateway, payload: AgentRunResult(state, returned)
    )

    response = next(iter(plugin_runner.RunAgent(_make_request(), None)))

    assert response.success is True
    assert [effect.type for effect in response.effects] == [EffectType.LOG]
    assert (response.agent_run.effects_returned, response.agent_run.effects_dropped) == (4, 3)


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_reports_the_tool_loop_in_its_summary(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Model and tool calls recorded during run() come back on the response, even on failure."""

    def _run(self: Any, state: Any, gateway: Any, payload: Any) -> AgentRunResult:
        recorder = current_recorder.get()
        assert recorder is not None
        recorder.reserve_model_call()
        recorder.record_tool_call(ToolCallRecord("echo", False, "ValueError", 12))
        recorder.record_stop("max_turns")
        raise RuntimeError("agent bug")

    monkeypatch.setattr(LOADED_PLUGINS[AGENT_KEY]["class"], "run", _run)

    response = next(iter(plugin_runner.RunAgent(_make_request(), None)))

    assert response.success is False
    summary = response.agent_run
    assert (summary.model_calls, summary.stop_reason) == (1, "max_turns")
    assert [(c.name, c.ok, c.error_type, c.duration_ms) for c in summary.tool_calls] == [
        ("echo", False, "ValueError", 12)
    ]
    assert current_recorder.get() is None


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_hook_failures_do_not_crash_the_run(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A hook that raises is logged and ignored — the agent's run still completes."""
    agent_cls = LOADED_PLUGINS[AGENT_KEY]["class"]

    def _hook_boom(self, *args):  # type: ignore[no-untyped-def]
        raise RuntimeError("observability bug")

    monkeypatch.setattr(agent_cls, "on_run_start", _hook_boom)
    monkeypatch.setattr(agent_cls, "on_run_end", _hook_boom)

    response = next(iter(plugin_runner.RunAgent(_make_request(), None)))
    # Run completed successfully despite both hooks raising.
    assert response.success is True
    assert response.error_kind == ""


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_past_its_deadline_saves_nothing_and_emits_nothing(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Once home-app's deadline passes, its lease can go to the next run, so this one stops."""
    agent_cls = LOADED_PLUGINS[AGENT_KEY]["class"]
    saved: list[str] = []
    monkeypatch.setattr(
        agent_cls, "save_state", lambda self, scope_key, state: saved.append(scope_key)
    )
    context = MagicMock()
    context.time_remaining.return_value = None
    context.is_active.return_value = False

    response = next(iter(plugin_runner.RunAgent(_make_request(), context)))

    assert response.success is False
    assert list(response.effects) == []
    assert saved == []


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_answers_busy_when_agent_runs_fill_their_share_of_workers(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Agent runs leave workers free for events; a run over the cap is turned away to retry."""
    slots = threading.BoundedSemaphore(1)
    monkeypatch.setattr(runner_module, "AGENT_RUN_SLOTS", slots)
    agent_cls = LOADED_PLUGINS[AGENT_KEY]["class"]
    loaded: list[str] = []
    original_load = agent_cls.load_state

    def _record_load(self, scope_key):  # type: ignore[no-untyped-def]
        loaded.append(scope_key)
        return original_load(self, scope_key)

    monkeypatch.setattr(agent_cls, "load_state", _record_load)

    assert slots.acquire(blocking=False)
    busy = next(iter(plugin_runner.RunAgent(_make_request(), None)))
    slots.release()
    served = next(iter(plugin_runner.RunAgent(_make_request(), None)))

    assert busy.success is False
    assert busy.error_kind == "RUNNER_BUSY"
    assert served.success is True
    assert len(loaded) == 1
    assert slots.acquire(blocking=False), "a finished run must give its slot back"


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_gives_the_tool_loop_the_calls_deadline_and_the_agents_ceiling(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The recorder the tool loop checks carries home-app's deadline and the agent's ceiling."""
    agent_cls = LOADED_PLUGINS[AGENT_KEY]["class"]
    monkeypatch.setattr(agent_cls, "max_model_calls", 7)
    seen: list[tuple[float | None, int | None]] = []
    original_run = agent_cls.run

    def _run(self: Any, state: Any, gateway: Any, payload: Any) -> AgentRunResult:
        recorder = current_recorder.get()
        assert recorder is not None
        seen.append((recorder.seconds_left(), recorder.max_model_calls))
        return original_run(self, state, gateway, payload)

    monkeypatch.setattr(agent_cls, "run", _run)
    context = MagicMock()
    context.time_remaining.return_value = 600.0
    context.is_active.return_value = True

    response = next(iter(plugin_runner.RunAgent(_make_request(), context)))

    assert response.success is True
    [(seconds_left, ceiling)] = seen
    assert seconds_left is not None and 560 < seconds_left <= 570
    assert ceiling == 7


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_stopped_by_its_deadline_saves_nothing_and_skips_sentry(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A run the tool loop stopped at its deadline fails quietly, without a half-saved state."""
    agent_cls = LOADED_PLUGINS[AGENT_KEY]["class"]
    saved: list[str] = []
    monkeypatch.setattr(
        agent_cls, "save_state", lambda self, scope_key, state: saved.append(scope_key)
    )

    def _run(self: Any, state: Any, gateway: Any, payload: Any) -> AgentRunResult:
        raise RunDeadlineExceeded("the run reached its deadline")

    monkeypatch.setattr(agent_cls, "run", _run)
    captured = MagicMock()
    monkeypatch.setattr(runner_module.sentry_sdk, "capture_exception", captured)

    response = next(iter(plugin_runner.RunAgent(_make_request(), None)))

    assert response.success is False
    assert list(response.effects) == []
    assert saved == []
    captured.assert_not_called()


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_a_run_that_raises_gives_its_slot_back(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failing agent must not hold its slot, or failures would starve later runs."""
    slots = threading.BoundedSemaphore(1)
    monkeypatch.setattr(runner_module, "AGENT_RUN_SLOTS", slots)

    def _boom(self: Any, state: Any, gateway: Any, payload: Any) -> AgentRunResult:
        raise RuntimeError("agent bug")

    monkeypatch.setattr(LOADED_PLUGINS[AGENT_KEY]["class"], "run", _boom)

    response = next(iter(plugin_runner.RunAgent(_make_request(), None)))

    assert response.success is False
    assert slots.acquire(blocking=False), "a failed run must give its slot back"


def _with_run_seconds(monkeypatch: pytest.MonkeyPatch, run_seconds: int) -> None:
    """Set the test agent's manifest `run_seconds` for this test."""
    loaded = LOADED_PLUGINS[AGENT_KEY]
    monkeypatch.setitem(
        loaded, "handler", {**(loaded.get("handler") or {}), "run_seconds": run_seconds}
    )


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_an_extended_run_waits_for_an_extended_slot_and_frees_its_agent_slot(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """With the extended share taken, a long run is turned away without holding a thread."""
    slots = threading.BoundedSemaphore(4)
    extended = threading.BoundedSemaphore(1)
    monkeypatch.setattr(runner_module, "AGENT_RUN_SLOTS", slots)
    monkeypatch.setattr(runner_module, "EXTENDED_AGENT_RUN_SLOTS", extended)
    _with_run_seconds(monkeypatch, 1200)

    assert extended.acquire(blocking=False)
    busy = next(iter(plugin_runner.RunAgent(_make_request(), None)))
    extended.release()
    served = next(iter(plugin_runner.RunAgent(_make_request(), None)))

    assert (busy.success, busy.error_kind) == (False, "EXTENDED_RUNS_BUSY")
    assert served.success is True
    assert all(slots.acquire(blocking=False) for _ in range(4)), "every agent slot is free again"
    assert extended.acquire(blocking=False), "the extended slot is free again"


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_a_run_at_the_default_time_needs_no_extended_slot(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Chat runs keep going while extended runs hold their whole share."""
    extended = threading.BoundedSemaphore(1)
    monkeypatch.setattr(runner_module, "EXTENDED_AGENT_RUN_SLOTS", extended)
    assert extended.acquire(blocking=False)

    response = next(iter(plugin_runner.RunAgent(_make_request(), None)))

    assert response.success is True


@pytest.mark.parametrize(
    ("run_seconds", "time_remaining", "expected"),
    [(1200, 1200.0, 1200), (900, 1200.0, 900), (1200, 600.0, 600)],
)
@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_a_run_gets_the_shorter_of_its_manifest_time_and_the_calls_timeout(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
    monkeypatch: pytest.MonkeyPatch,
    run_seconds: int,
    time_remaining: float,
    expected: int,
) -> None:
    """The tool loop stops by the agent's own time, and caps its total tool output."""
    _with_run_seconds(monkeypatch, run_seconds)
    agent_cls = LOADED_PLUGINS[AGENT_KEY]["class"]
    seen: list[tuple[float | None, int | None]] = []
    original_run = agent_cls.run

    def _run(self: Any, state: Any, gateway: Any, payload: Any) -> AgentRunResult:
        recorder = current_recorder.get()
        assert recorder is not None
        seen.append((recorder.seconds_left(), recorder.max_tool_result_chars))
        return original_run(self, state, gateway, payload)

    monkeypatch.setattr(agent_cls, "run", _run)
    context = MagicMock()
    context.time_remaining.return_value = time_remaining
    context.is_active.return_value = True

    response = next(iter(plugin_runner.RunAgent(_make_request(), context)))

    assert response.success is True
    [(seconds_left, total)] = seen
    latest = expected - DEADLINE_MARGIN_SECONDS
    assert seconds_left is not None and latest - 10 < seconds_left <= latest
    assert total == RUN_TOOL_RESULT_CHARS


@pytest.mark.parametrize(
    ("requested", "agent_runs", "expected"),
    [(None, 4, 1), ("2", 4, 2), ("9", 4, 3), ("3", 1, 1), ("0", 4, 1)],
)
def test_extended_runs_always_leave_an_agent_run_for_the_others(
    requested: str | None, agent_runs: int, expected: int
) -> None:
    """However the instance is configured, extended runs cannot take every agent thread."""
    assert extended_agent_run_limit(requested, agent_runs) == expected


def _with_progress(monkeypatch: pytest.MonkeyPatch, level: str | None) -> None:
    """Set the test agent's manifest `progress` for this test."""
    loaded = LOADED_PLUGINS[AGENT_KEY]
    handler = {**(loaded.get("handler") or {})}
    handler.pop("progress", None)
    if level is not None:
        handler["progress"] = level
    monkeypatch.setitem(loaded, "handler", handler)


def _reporting_run(monkeypatch: pytest.MonkeyPatch, threads: list[int]) -> None:
    """Make the test agent report one tool call and outlast a heartbeat."""
    monkeypatch.setattr(runner_module, "HEARTBEAT_SECONDS", 0.05)
    monkeypatch.setattr(runner_module, "PROGRESS_POLL_SECONDS", 0.01)
    agent_cls = LOADED_PLUGINS[AGENT_KEY]["class"]
    original_run = agent_cls.run

    def _run(self: Any, state: Any, gateway: Any, payload: Any) -> AgentRunResult:
        threads.append(threading.get_ident())
        recorder = current_recorder.get()
        assert recorder is not None, "the run's recorder follows it onto its thread"
        recorder.phase = "working"
        recorder.report_tool("tool_started", "Reading lab results")
        time.sleep(0.15)
        recorder.report_tool("tool_finished", "Reading lab results", ok=True)
        return original_run(self, state, gateway, payload)

    monkeypatch.setattr(agent_cls, "run", _run)


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_a_streamed_run_reports_its_tools_and_heartbeats_before_its_result(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """With "activity", the person waiting sees each tool's label and that the run is alive."""
    _with_progress(monkeypatch, "activity")
    threads: list[int] = []
    _reporting_run(monkeypatch, threads)

    responses = list(plugin_runner.RunAgent(_make_request(stream_progress=True), None))

    *progress, final = responses
    assert final.success is True and not final.HasField("progress")
    assert len(final.effects) == 1
    assert all(response.HasField("progress") for response in progress)
    kinds = [response.progress.kind for response in progress]
    assert "heartbeat" in kinds
    tools = [
        (r.progress.kind, r.progress.label, r.progress.ok)
        for r in progress
        if r.progress.kind != "heartbeat"
    ]
    assert tools == [
        ("tool_started", "Reading lab results", False),
        ("tool_finished", "Reading lab results", True),
    ]
    assert {r.progress.phase for r in progress} <= {"thinking", "working"}
    elapsed = [r.progress.elapsed_ms for r in progress]
    assert elapsed == sorted(elapsed)
    assert threads and threads[0] != threading.get_ident(), "the agent ran on its own thread"


@pytest.mark.parametrize("level", [None, "status"])
@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_an_agent_at_the_status_level_streams_heartbeats_only(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
    monkeypatch: pytest.MonkeyPatch,
    level: str | None,
) -> None:
    """Tool labels never leave the runner unless the manifest asks for "activity"."""
    _with_progress(monkeypatch, level)
    _reporting_run(monkeypatch, [])

    *progress, final = plugin_runner.RunAgent(_make_request(stream_progress=True), None)

    assert final.success is True
    assert progress and {r.progress.kind for r in progress} == {"heartbeat"}
    assert {r.progress.label for r in progress} == {""}


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_a_run_not_asked_to_stream_answers_once(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A home-app that does not ask for progress gets only the final response."""
    _with_progress(monkeypatch, "activity")
    threads: list[int] = []
    _reporting_run(monkeypatch, threads)

    responses = list(plugin_runner.RunAgent(_make_request(), None))

    assert len(responses) == 1 and responses[0].success is True
    assert threads == [threading.get_ident()]


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_a_streamed_run_that_fails_ends_with_its_failure_and_frees_its_slot(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A run that raises on its thread still answers, and gives its slot back."""
    slots = threading.BoundedSemaphore(1)
    monkeypatch.setattr(runner_module, "AGENT_RUN_SLOTS", slots)

    def _boom(self: Any, state: Any, gateway: Any, payload: Any) -> AgentRunResult:
        raise RuntimeError("agent bug")

    monkeypatch.setattr(LOADED_PLUGINS[AGENT_KEY]["class"], "run", _boom)

    responses = list(plugin_runner.RunAgent(_make_request(stream_progress=True), None))

    assert responses[-1].success is False and not responses[-1].HasField("progress")
    assert slots.acquire(blocking=False), "a failed run must give its slot back"


@pytest.mark.parametrize(("level", "streams_text"), [("reply", True), ("activity", False)])
@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_reply_text_is_streamed_only_at_the_reply_level(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
    monkeypatch: pytest.MonkeyPatch,
    level: str,
    streams_text: bool,
) -> None:
    """At "reply" the text arrives as it is written; at "activity" it never leaves."""
    _with_progress(monkeypatch, level)
    monkeypatch.setattr(runner_module, "PROGRESS_POLL_SECONDS", 0.01)
    agent_cls = LOADED_PLUGINS[AGENT_KEY]["class"]
    original_run = agent_cls.run

    def _run(self: Any, state: Any, gateway: Any, payload: Any) -> AgentRunResult:
        recorder = current_recorder.get()
        assert recorder is not None
        recorder.report_turn()
        recorder.report_text("Three records ")
        time.sleep(0.05)
        recorder.report_text("need review.")
        return original_run(self, state, gateway, payload)

    monkeypatch.setattr(agent_cls, "run", _run)

    *progress, final = plugin_runner.RunAgent(_make_request(stream_progress=True), None)

    assert final.success is True
    texts = [r.progress.text for r in progress if r.progress.kind == "text"]
    if streams_text:
        assert "".join(texts) == "Three records need review."
        assert {r.progress.phase for r in progress if r.progress.kind == "text"} == {"writing"}
        assert progress[0].progress.kind == "turn_started"
    else:
        assert texts == []
        assert "turn_started" not in {r.progress.kind for r in progress}


class _NotAnAgent:
    """A handler-like class a plugin loads alongside its agents; records being built."""

    instantiated: list[object] = []

    def __init__(self) -> None:
        _NotAnAgent.instantiated.append(self)


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_refuses_a_loaded_class_that_is_not_an_agent(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    inference_gateway_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Only a class the plugin declares as an agent runs; a handler named as one does not."""
    handler_id = "test_agent_plugin.handlers.trigger:Trigger"
    monkeypatch.setitem(
        LOADED_PLUGINS,
        f"test_agent_plugin:{handler_id}",
        {**LOADED_PLUGINS[AGENT_KEY], "class": _NotAnAgent},
    )

    _NotAnAgent.instantiated.clear()

    response = next(iter(plugin_runner.RunAgent(_make_request(agent_id=handler_id), None)))

    assert response.success is False
    assert _NotAnAgent.instantiated == []
