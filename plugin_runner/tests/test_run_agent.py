import json
from pathlib import Path
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
    """Emitted effects carry plugin_name, classname, handler_name, actor, source."""
    request = _make_request(
        plugin_name="test_agent_plugin",
        handler_name="EchoTrigger",
        actor="42",
        source="handler",
    )
    response = next(iter(plugin_runner.RunAgent(request, None)))

    effect = response.effects[0]
    assert effect.plugin_name == "test_agent_plugin"
    assert effect.classname == "EchoAgent"
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
