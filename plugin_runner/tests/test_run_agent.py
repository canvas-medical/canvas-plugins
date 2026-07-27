import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_generated.messages.plugins_pb2 import RunAgentRequest
from plugin_runner.plugin_runner import (
    EVENT_HANDLER_MAP,
    LOADED_PLUGINS,
    PluginRunner,
)

AGENT_KEY = "test_agent_plugin:test_agent_plugin.agents.echo_agent:EchoAgent"
AGENT_ID = "test_agent_plugin.agents.echo_agent:EchoAgent"


@pytest.fixture
def plugin_runner() -> PluginRunner:
    """Construct a PluginRunner with statsd mocked out for unit tests."""
    runner = PluginRunner()
    runner.statsd_client = MagicMock()  # type: ignore[attr-defined]
    return runner


@pytest.fixture
def anthropic_plugin_secrets(load_test_plugins: None) -> None:
    """Populate the loaded test agent's secrets dict with the Anthropic key.

    The RunAgent RPC builds the LLMGateway from ``plugin["secrets"]``; in
    production those values come from the plugin's manifest variables and
    the customer's admin config. Tests inject them directly into
    LOADED_PLUGINS after the plugin loads.
    """
    LOADED_PLUGINS[AGENT_KEY]["secrets"] = {
        "ANTHROPIC_API_KEY": "sk-test-runner",
        "ANTHROPIC_MODEL": "claude-sonnet-4-6",
    }


def _make_request(
    *,
    agent_id: str = AGENT_ID,
    scope_key: str = "test_agent_plugin:patient:p1",
    trigger_payload: str = '{"note_id": "n1"}',
    plugin_name: str = "test_agent_plugin",
    handler_name: str = "EchoTrigger",
    actor: str = "1",
    source: str = "handler",
) -> RunAgentRequest:
    return RunAgentRequest(
        agent_id=agent_id,
        scope_key=scope_key,
        run_id="run-1",
        trigger_payload=trigger_payload,
        plugin_name=plugin_name,
        handler_name=handler_name,
        actor=actor,
        source=source,
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
    anthropic_plugin_secrets: None,
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
        "loaded_with": "test_agent_plugin:patient:p1",
        "trigger": {"note_id": "n1"},
        "gateway_model": "claude-sonnet-4-6",
    }


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_stamps_provenance_on_emitted_effects(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    anthropic_plugin_secrets: None,
) -> None:
    """Emitted effects carry plugin_name, handler_name, actor, source.

    ``classname`` is intentionally left empty on agent-emitted effects
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
    assert effect.handler_name == "EchoTrigger"
    assert effect.actor == "42"
    assert effect.source == "handler"


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_defaults_source_to_agent_when_request_omits_it(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    anthropic_plugin_secrets: None,
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
    anthropic_plugin_secrets: None,
) -> None:
    """A well-formed agent_id that isn't in LOADED_PLUGINS yields success=False."""
    request = _make_request(agent_id="test_agent_plugin.agents.echo_agent:NoSuchClass")
    response = next(iter(plugin_runner.RunAgent(request, None)))
    assert response.success is False
    assert list(response.effects) == []


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_missing_api_key_short_circuits(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
) -> None:
    """Without the ANTHROPIC_API_KEY plugin secret, the RPC refuses to dispatch."""
    # Leave secrets empty — the plugin install path would normally populate
    # them from the customer's admin config; here we just don't set them.
    LOADED_PLUGINS[AGENT_KEY]["secrets"] = {}
    response = next(iter(plugin_runner.RunAgent(_make_request(), None)))
    assert response.success is False
    assert list(response.effects) == []


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_invalid_trigger_payload_json(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    anthropic_plugin_secrets: None,
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
    anthropic_plugin_secrets: None,
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
def test_run_agent_serializes_via_scope_key_lock(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    anthropic_plugin_secrets: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Two RPC invocations sharing a scope_key serialize; the loser tags the response.

    Sets up a re-entrant scenario: the agent's run() itself tries to
    acquire the same scope_key lock that the outer RunAgent RPC already
    holds. The inner attempt raises AgentLocked, which the RunAgent
    handler catches and reports as success=False with
    error_kind='AGENT_LOCKED' so the home-app side can recognize it as
    retryable-with-backoff (doc §6.2).
    """
    from canvas_sdk.agents import agent_lock as agent_lock_helper

    agent_cls = LOADED_PLUGINS[AGENT_KEY]["class"]
    scope_key = "test_agent_plugin:patient:p1"

    def _re_enter(self, state, gateway, trigger_payload):  # type: ignore[no-untyped-def]
        with agent_lock_helper(scope_key):
            pytest.fail("Inner lock acquisition should have raised AgentLocked")

    monkeypatch.setattr(agent_cls, "run", _re_enter)
    response = next(iter(plugin_runner.RunAgent(_make_request(scope_key=scope_key), None)))
    assert response.success is False
    assert list(response.effects) == []
    assert response.error_kind == "AGENT_LOCKED"


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_does_not_set_error_kind_on_generic_failure(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    anthropic_plugin_secrets: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A generic exception inside the agent leaves error_kind empty.

    error_kind is reserved for *expected* failure modes the caller should
    react to specifically (currently just AGENT_LOCKED). Unstructured
    exceptions still surface as success=False, but error_kind must stay
    empty so the caller doesn't mistake them for retryable contention.
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
    anthropic_plugin_secrets: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Successful runs invoke on_run_start then on_run_end (no on_run_error)."""
    from canvas_sdk.agents import AgentRunResult

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
    assert call_log[0][1] == "test_agent_plugin:patient:p1"
    assert isinstance(call_log[1][1], AgentRunResult)


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_fires_on_run_error_when_run_raises(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    anthropic_plugin_secrets: None,
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


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_does_not_fire_hooks_on_lock_contention(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    anthropic_plugin_secrets: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Lock contention shouldn't fire lifecycle hooks — the agent never started."""
    from canvas_sdk.agents import agent_lock as agent_lock_helper

    agent_cls = LOADED_PLUGINS[AGENT_KEY]["class"]
    scope_key = "test_agent_plugin:patient:p1"
    call_log: list[str] = []

    monkeypatch.setattr(agent_cls, "on_run_start", lambda self, sk: call_log.append("on_run_start"))
    monkeypatch.setattr(agent_cls, "on_run_end", lambda self, r: call_log.append("on_run_end"))
    monkeypatch.setattr(agent_cls, "on_run_error", lambda self, e: call_log.append("on_run_error"))

    def _re_enter(self, state, gateway, trigger_payload):  # type: ignore[no-untyped-def]
        # Inner lock acquisition raises AgentLocked because the outer
        # RunAgent already holds it. The contention path returns before
        # any of the hooks fire on the inner attempt.
        with agent_lock_helper(scope_key):
            pass

    monkeypatch.setattr(agent_cls, "run", _re_enter)
    response = next(iter(plugin_runner.RunAgent(_make_request(scope_key=scope_key), None)))
    assert response.success is False
    assert response.error_kind == "AGENT_LOCKED"
    # on_run_start fired for the outer run; on_run_error fired when its
    # run() (the re-entry attempt) raised. on_run_end must NOT have fired.
    assert "on_run_end" not in call_log


# ---------------------------------------------------------------------------
# tools_allowed injection from the manifest
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_sets_tools_allowed_from_manifest(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    anthropic_plugin_secrets: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``components.agents[].tools.allowed`` lands on the agent as a frozenset."""
    # Splice tools.allowed into the loaded manifest entry. Real plugins
    # declare this statically in CANVAS_MANIFEST.json; we mutate at runtime
    # so the test doesn't need its own fixture plugin.
    LOADED_PLUGINS[AGENT_KEY]["handler"]["tools"] = {"allowed": ["find_medications", "create_task"]}

    agent_cls = LOADED_PLUGINS[AGENT_KEY]["class"]
    captured: dict[str, Any] = {}

    def _capture(self, state, gateway, trigger_payload):  # type: ignore[no-untyped-def]
        from canvas_sdk.agents import AgentRunResult

        captured["tools_allowed"] = self.tools_allowed
        return AgentRunResult(state=state, effects=[])

    monkeypatch.setattr(agent_cls, "run", _capture)
    next(iter(plugin_runner.RunAgent(_make_request(), None)))

    assert captured["tools_allowed"] == frozenset({"find_medications", "create_task"})


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_scopes_agent_tools_to_manifest_allowlist(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    anthropic_plugin_secrets: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Platform substitutes a scoped registry on the agent before run() fires.

    The agent's `self.tools` is the manifest-scoped view, not the full
    registry the class was declared with. Disallowed tools are dropped
    entirely (their executors aren't reachable from the scoped registry).
    """
    from canvas_sdk.agents import AgentRunResult, ToolRegistry

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
def test_run_agent_skips_scoping_when_tools_allowed_is_none(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    anthropic_plugin_secrets: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """No manifest declaration → agent.tools stays as the class-level registry."""
    from canvas_sdk.agents import AgentRunResult, ToolRegistry

    full_registry = ToolRegistry()
    full_registry.register(
        {"name": "read_chart", "description": "x", "input_schema": {"type": "object"}},
        lambda arguments, *, ctx: None,
    )

    agent_cls = LOADED_PLUGINS[AGENT_KEY]["class"]
    monkeypatch.setattr(agent_cls, "tools", full_registry, raising=False)
    LOADED_PLUGINS[AGENT_KEY]["handler"].pop("tools", None)

    captured: dict[str, Any] = {}

    def _capture(self, state, gateway, trigger_payload):  # type: ignore[no-untyped-def]
        captured["is_same_object"] = self.tools is full_registry
        return AgentRunResult(state=state, effects=[])

    monkeypatch.setattr(agent_cls, "run", _capture)
    next(iter(plugin_runner.RunAgent(_make_request(), None)))

    # No scoping happened — the agent saw the unfiltered class-level registry.
    assert captured["is_same_object"] is True


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_leaves_tools_allowed_none_when_manifest_omits_it(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    anthropic_plugin_secrets: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """No manifest declaration → tools_allowed is None (= no filtering)."""
    # Test fixture's manifest declares no ``tools`` key. Make sure we don't
    # invent a filter when the author didn't ask for one.
    LOADED_PLUGINS[AGENT_KEY]["handler"].pop("tools", None)

    agent_cls = LOADED_PLUGINS[AGENT_KEY]["class"]
    captured: dict[str, Any] = {}

    def _capture(self, state, gateway, trigger_payload):  # type: ignore[no-untyped-def]
        from canvas_sdk.agents import AgentRunResult

        captured["tools_allowed"] = self.tools_allowed
        return AgentRunResult(state=state, effects=[])

    monkeypatch.setattr(agent_cls, "run", _capture)
    next(iter(plugin_runner.RunAgent(_make_request(), None)))

    assert captured["tools_allowed"] is None


@pytest.mark.parametrize("install_test_plugin", ["test_agent_plugin"], indirect=True)
def test_run_agent_hook_failures_do_not_crash_the_run(
    install_test_plugin: Path,
    load_test_plugins: None,
    plugin_runner: PluginRunner,
    anthropic_plugin_secrets: None,
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
