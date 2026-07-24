import json

import pytest
from pydantic import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_generated.messages.plugins_pb2 import RunAgentRequest
from canvas_sdk.effects.agent import RunAgentEffect


def test_run_agent_effect_type_is_run_agent() -> None:
    """RunAgentEffect.apply() produces an Effect with type RUN_AGENT."""
    effect = RunAgentEffect(
        agent_id="my_plugin.agents.x:Agent",
        scope_key="my_plugin:x:patient:p1",
    ).apply()
    assert effect.type == EffectType.RUN_AGENT


def test_run_agent_effect_payload_contains_all_three_fields() -> None:
    """Payload's data block carries agent_id, scope_key, trigger_payload."""
    effect = RunAgentEffect(
        agent_id="my_plugin.agents.x:Agent",
        scope_key="my_plugin:x:patient:p1",
        trigger_payload={"note_id": "n1", "patient_id": "p1"},
    ).apply()

    data = json.loads(effect.payload)["data"]
    assert data == {
        "agent_id": "my_plugin.agents.x:Agent",
        "scope_key": "my_plugin:x:patient:p1",
        "trigger_payload": {"note_id": "n1", "patient_id": "p1"},
    }


def test_run_agent_effect_trigger_payload_defaults_to_empty_dict() -> None:
    """Omitting trigger_payload should serialize as {}, not null or absent."""
    effect = RunAgentEffect(
        agent_id="my_plugin.agents.x:Agent",
        scope_key="my_plugin:x:patient:p1",
    ).apply()

    data = json.loads(effect.payload)["data"]
    assert data["trigger_payload"] == {}


def test_run_agent_effect_rejects_empty_agent_id() -> None:
    """An empty agent_id is a programmer error, not a runtime case to recover from."""
    with pytest.raises(ValidationError):
        RunAgentEffect(agent_id="", scope_key="any")


def test_run_agent_effect_rejects_empty_scope_key() -> None:
    """An empty scope_key would collapse lock/state namespacing — reject at construction."""
    with pytest.raises(ValidationError):
        RunAgentEffect(agent_id="any", scope_key="")


def test_effect_type_run_agent_enum_value_is_pinned() -> None:
    """RUN_AGENT must stay at 11000 to keep the wire format stable.

    Changing this number breaks every running plugin runner / home-app
    consumer that hasn't redeployed. If you really need to renumber, this
    test failing is the deliberate gate.
    """
    assert int(EffectType.RUN_AGENT) == 11000


def test_run_agent_request_roundtrip() -> None:
    """RunAgentRequest survives a SerializeToString/FromString roundtrip with all fields."""
    request = RunAgentRequest(
        agent_id="my_plugin.agents.x:Agent",
        scope_key="my_plugin:x:patient:p1",
        run_id="run-abc",
        trigger_payload='{"note_id": "n1"}',
        plugin_name="my_plugin",
        handler_name="TriggerHandler",
        actor="1",
        source="handler",
    )

    wire = request.SerializeToString()
    decoded = RunAgentRequest.FromString(wire)

    assert decoded.agent_id == "my_plugin.agents.x:Agent"
    assert decoded.scope_key == "my_plugin:x:patient:p1"
    assert decoded.run_id == "run-abc"
    assert decoded.trigger_payload == '{"note_id": "n1"}'
    assert decoded.plugin_name == "my_plugin"
    assert decoded.handler_name == "TriggerHandler"
    assert decoded.actor == "1"
    assert decoded.source == "handler"
