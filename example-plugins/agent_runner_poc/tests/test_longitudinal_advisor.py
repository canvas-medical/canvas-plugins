import json

import pytest
from agent_runner_poc.agents.longitudinal_advisor import LongitudinalCareAdvisor

from canvas_sdk.agents import RunSubject
from canvas_sdk.effects import EffectType
from canvas_sdk.test_utils.agents import (
    FakeGateway,
    prepare_agent,
    reply,
    run_agent,
    text,
    tool_use,
)
from canvas_sdk.test_utils.factories import NoteFactory, PatientFactory

# The advisor's grant in CANVAS_MANIFEST.json.
GRANT = ["@clinical_reads", "@clinical_alerts"]


@pytest.mark.django_db
def test_the_advisor_stages_a_card_for_new_follow_up() -> None:
    """A card the model stages is an effect the advisor's grant lets the platform apply."""
    patient = PatientFactory.create()
    note = NoteFactory.create(patient=patient)
    agent = prepare_agent(
        LongitudinalCareAdvisor,
        allowed=GRANT,
        subject=RunSubject(patient_id=patient.id, note_id=str(note.id)),
    )
    gateway = FakeGateway(
        reply(tool_use("find_conditions")),
        reply(
            tool_use(
                "add_or_update_protocol_card",
                {"title": "Recheck A1c", "narrative": "Last A1c was 9.2.", "status": "due"},
            )
        ),
        reply(text("Staged one card.")),
    )

    run = run_agent(agent, gateway)

    assert [effect.type for effect in run.effects] == [EffectType.ADD_OR_UPDATE_PROTOCOL_CARD]
    assert json.loads(run.effects[0].payload)["data"]["title"] == "Recheck A1c"
    assert [call.name for call in run.tool_calls] == [
        "find_conditions",
        "add_or_update_protocol_card",
    ]
    assert all(call.ok for call in run.tool_calls)


@pytest.mark.django_db
def test_the_advisor_never_sends_the_patients_name() -> None:
    """The tools are already scoped to the patient, so the prompt needs no identifiers."""
    patient = PatientFactory.create(first_name="Zelda", last_name="Quartermaine")
    agent = prepare_agent(
        LongitudinalCareAdvisor, allowed=GRANT, subject=RunSubject(patient_id=patient.id)
    )
    gateway = FakeGateway(reply(text("Nothing to follow up.")))

    run_agent(agent, gateway)

    sent = json.dumps(gateway.requests[0]["messages"])
    assert "Zelda" not in sent and "Quartermaine" not in sent
