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
        scope=RunAgentEffect.Scope.AGENT,
    ).apply()
    assert effect.type == EffectType.RUN_AGENT


def test_run_agent_effect_payload_carries_the_subject_and_scope() -> None:
    """The data block carries the agent, scope, subject, and payload for home-app."""
    effect = RunAgentEffect(
        agent_id="my_plugin.agents.x:Agent",
        scope=RunAgentEffect.Scope.PATIENT,
        patient_id="p1",
        note_id="n1",
        trigger_payload={"reason": "locked"},
    ).apply()

    data = json.loads(effect.payload)["data"]
    assert data == {
        "agent_id": "my_plugin.agents.x:Agent",
        "scope": "patient",
        "patient_id": "p1",
        "note_id": "n1",
        "trigger_payload": {"reason": "locked"},
    }


def test_run_agent_effect_defaults_to_no_subject_and_an_empty_payload() -> None:
    """Omitted subject fields serialize as null and the payload as {}."""
    effect = RunAgentEffect(
        agent_id="my_plugin.agents.x:Agent",
        scope=RunAgentEffect.Scope.AGENT,
    ).apply()

    data = json.loads(effect.payload)["data"]
    assert data["patient_id"] is None
    assert data["note_id"] is None
    assert data["trigger_payload"] == {}


def test_run_agent_effect_rejects_empty_agent_id() -> None:
    """An empty agent_id is a programmer error, not a runtime case to recover from."""
    with pytest.raises(ValidationError):
        RunAgentEffect(agent_id="", scope=RunAgentEffect.Scope.AGENT)


def test_run_agent_effect_requires_a_scope() -> None:
    """The scope decides which runs wait on each other, so there is no default."""
    with pytest.raises(ValidationError):
        RunAgentEffect(agent_id="any")  # type: ignore[call-arg]


@pytest.mark.parametrize(
    "scope",
    [
        RunAgentEffect.Scope.PATIENT,
        RunAgentEffect.Scope.PATIENT_AND_STAFF,
        RunAgentEffect.Scope.NOTE,
    ],
)
def test_patient_scopes_require_a_patient(scope: RunAgentEffect.Scope) -> None:
    """A scope keyed on the patient cannot be derived without one."""
    with pytest.raises(ValidationError, match="requires 'patient_id'"):
        RunAgentEffect(agent_id="any", scope=scope, note_id="n1")


def test_note_scope_requires_a_note() -> None:
    """The note scope is keyed on the note."""
    with pytest.raises(ValidationError, match="requires 'note_id'"):
        RunAgentEffect(agent_id="any", scope=RunAgentEffect.Scope.NOTE, patient_id="p1")


def test_a_note_requires_its_patient() -> None:
    """The platform checks the note belongs to the patient, so both are needed."""
    with pytest.raises(ValidationError, match="'note_id' requires 'patient_id'"):
        RunAgentEffect(agent_id="any", scope=RunAgentEffect.Scope.AGENT, note_id="n1")


@pytest.mark.parametrize("key", ["patient_id", "staff_id", "note_id"])
def test_the_subject_cannot_travel_in_the_trigger_payload(key: str) -> None:
    """The agent reads the subject from self.subject, never from the payload."""
    with pytest.raises(ValidationError, match=key):
        RunAgentEffect(
            agent_id="any",
            scope=RunAgentEffect.Scope.AGENT,
            trigger_payload={key: "x", "message": "hi"},
        )


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
        scope_key="patient:p1",
        run_id="run-abc",
        trigger_payload='{"reason": "locked"}',
        plugin_name="my_plugin",
        handler_name="TriggerHandler",
        actor="1",
        source="handler",
        patient_id="p1",
        staff_id="s1",
        note_id="n1",
    )

    decoded = RunAgentRequest.FromString(request.SerializeToString())

    assert decoded == request
