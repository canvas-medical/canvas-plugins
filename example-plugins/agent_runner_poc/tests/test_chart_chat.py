import pytest
from agent_runner_poc.agents.chart_chat import ChartChatAgent, load_conversation_messages

from canvas_sdk.agents import AgentPlugin, RunSubject
from canvas_sdk.test_utils.agents import (
    FakeGateway,
    prepare_agent,
    reply,
    run_agent,
    text,
    tool_use,
)
from canvas_sdk.test_utils.factories import PatientFactory, StaffFactory


def _agent_for(patient_id: str, staff_id: str) -> AgentPlugin:
    """A chat agent for one clinician's run on one patient, as the platform sets it up."""
    return prepare_agent(
        ChartChatAgent, subject=RunSubject(patient_id=patient_id, staff_id=staff_id)
    )


@pytest.mark.django_db
def test_each_clinician_has_their_own_conversation() -> None:
    """One clinician's chat never becomes another's context."""
    patient = PatientFactory.create()
    first = _agent_for(patient.id, StaffFactory.create().id)
    second = _agent_for(patient.id, StaffFactory.create().id)

    state = first.load_state("patient_and_staff")
    state.data["messages"] = [{"role": "user", "content": "How is her A1c trending?"}]
    first.save_state("patient_and_staff", state)

    assert second.load_state("patient_and_staff").data["messages"] == []
    assert first.load_state("patient_and_staff").data["messages"] == [
        {"role": "user", "content": "How is her A1c trending?"}
    ]


@pytest.mark.django_db
def test_run_answers_through_the_tool_loop_and_keeps_the_transcript() -> None:
    """The agent stores the clinician's turn, the tool exchange, and the answer."""
    patient, staff = PatientFactory.create(), StaffFactory.create()
    agent = prepare_agent(
        ChartChatAgent,
        allowed=["get_patient_demographics"],
        subject=RunSubject(patient_id=patient.id, staff_id=staff.id),
    )
    gateway = FakeGateway(
        reply(tool_use("get_patient_demographics")),
        reply(text("She is 54.")),
    )

    run = run_agent(agent, gateway, {"user_message": "How old is she?"})

    saved = load_conversation_messages(patient.id, staff.id)
    assert [message["role"] for message in saved] == ["user", "assistant", "user", "assistant"]
    assert saved[0] == {"role": "user", "content": "How old is she?"}
    assert saved[-1]["content"][0]["text"] == "She is 54."
    assert [call.name for call in run.tool_calls] == ["get_patient_demographics"]


@pytest.mark.django_db
def test_a_long_conversation_keeps_only_its_newest_part(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The stored row stops growing, and what it keeps starts on a question."""
    monkeypatch.setattr("agent_runner_poc.agents.chart_chat.STORED_HISTORY_CHARS", 200)
    agent = _agent_for(PatientFactory.create().id, StaffFactory.create().id)
    turns = [
        message
        for index in range(10)
        for message in (
            {"role": "user", "content": f"question {index}"},
            {"role": "assistant", "content": [{"type": "text", "text": f"answer {index}"}]},
        )
    ]

    state = agent.load_state("patient_and_staff")
    state.data["messages"] = turns
    agent.save_state("patient_and_staff", state)

    stored = agent.load_state("patient_and_staff").data["messages"]
    assert 0 < len(stored) < len(turns)
    assert stored == turns[-len(stored) :]
    assert stored[0]["role"] == "user" and isinstance(stored[0]["content"], str)
