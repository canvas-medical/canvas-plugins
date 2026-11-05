import json

import pytest
from canvas__agent_runner_poc.agents.longitudinal_advisor import LongitudinalCareAdvisor

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
from canvas_sdk.test_utils.factories import NoteFactory, PatientFactory, ProtocolCurrentFactory

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


@pytest.mark.django_db
def test_the_advisor_starts_from_its_own_cards_read_through_find_protocol_cards() -> None:
    """The run is briefed with this plugin's cards, as the tool returns them, and no others."""
    patient = PatientFactory.create()
    ProtocolCurrentFactory.create(
        patient=patient,
        plugin_name="canvas__agent_runner_poc",
        protocol_key="recheck-a1c",
        title="Recheck A1c",
    )
    ProtocolCurrentFactory.create(patient=patient, plugin_name="another_plugin", title="Not ours")
    ProtocolCurrentFactory.create(plugin_name="canvas__agent_runner_poc", title="Another patient's")
    agent = prepare_agent(
        LongitudinalCareAdvisor, allowed=GRANT, subject=RunSubject(patient_id=patient.id)
    )

    state = agent.load_state("patient")
    gateway = FakeGateway(reply(text("Nothing new.")))
    run_agent(agent, gateway)

    assert [(card["protocol_key"], card["title"]) for card in state.data["cards"]] == [
        ("recheck-a1c", "Recheck A1c")
    ]
    sent = gateway.requests[0]["messages"][0]["content"]
    assert '"protocol_key": "recheck-a1c"' in sent
    assert "Not ours" not in sent and "Another patient's" not in sent


@pytest.mark.django_db
def test_the_advisor_cannot_start_without_the_grant_that_reads_its_cards() -> None:
    """Its state comes through find_protocol_cards, so a deployment that removes the grant fails loudly."""
    patient = PatientFactory.create()
    agent = prepare_agent(
        LongitudinalCareAdvisor,
        allowed=["@clinical_alerts"],
        subject=RunSubject(patient_id=patient.id),
    )

    with pytest.raises(ValueError, match="find_protocol_cards"):
        agent.load_state("patient")
