import json
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest
from agent_runner_poc.agents.chart_chat import (
    DECISIONS_NOTE_PREFIX,
    ChartChatAgent,
    load_conversation_messages,
)

from canvas_sdk.agents import AgentPlugin, RunRequester, RunSubject
from canvas_sdk.effects import EffectType
from canvas_sdk.test_utils.agents import (
    FakeGateway,
    prepare_agent,
    reply,
    run_agent,
    text,
    tool_use,
)
from canvas_sdk.test_utils.factories import PatientFactory, StaffFactory
from canvas_sdk.v1.data import AgentRun, AgentRunProposal, AgentRunProposalStatus, AgentRunStatus


def _agent_for(patient_id: str, staff_id: str) -> AgentPlugin:
    """A chat agent for one clinician's run on one patient, as the platform sets it up."""
    return prepare_agent(
        ChartChatAgent,
        subject=RunSubject(patient_id=patient_id),
        requester=RunRequester(staff_id=staff_id),
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
        subject=RunSubject(patient_id=patient.id),
        requester=RunRequester(staff_id=staff.id),
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


@pytest.mark.django_db
def test_a_task_the_clinician_asks_for_waits_for_their_approval() -> None:
    """With the manifest's approval list, create_task proposes the task instead of making it."""
    patient, staff = PatientFactory.create(), StaffFactory.create()
    agent = prepare_agent(
        ChartChatAgent,
        allowed=["create_task"],
        approve=["@task_writes"],
        subject=RunSubject(patient_id=patient.id),
        requester=RunRequester(staff_id=staff.id),
    )
    gateway = FakeGateway(
        reply(tool_use("create_task", {"title": "Call about labs"})),
        reply(text("The task is waiting for your approval below.")),
    )

    run = run_agent(agent, gateway, {"user_message": "Add a task to call her about labs."})

    (proposal,) = run.effects
    assert proposal.type == EffectType.PROPOSE_AGENT_ACTION
    assert [e["type"] for e in json.loads(proposal.payload)["data"]["effects"]] == ["CREATE_TASK"]
    tool_result = gateway.requests[1]["messages"][-1]["content"][0]["content"]
    assert json.loads(tool_result)["status"] == "awaiting_approval"


def _proposal(staff: Any, status: str, reason: str = "") -> AgentRunProposal:
    """A proposal the chat agent made for ``staff``, decided as ``status``."""
    run = AgentRun.objects.create(
        id=uuid4(),
        plugin_name="agent_runner_poc",
        agent_id="agent_runner_poc.agents.chart_chat:ChartChatAgent",
        handler_name="agent_runner_poc.applications.chart_chat:ChartChatAPI",
        scope="patient_and_staff",
        scope_key="k",
        staff=staff,
        status=AgentRunStatus.SUCCEEDED,
        error_kind="",
        error="",
        queued_at=datetime(2026, 10, 31, tzinfo=UTC),
        attempts=0,
        stop_reason="",
        capabilities=[],
    )
    return AgentRunProposal.objects.create(
        id=uuid4(),
        run=run,
        plugin_name="agent_runner_poc",
        agent_id="agent_runner_poc.agents.chart_chat:ChartChatAgent",
        tool="create_task",
        arguments={"title": "Call about labs"},
        effect_types=["CREATE_TASK"],
        staff=staff,
        status=status,
        created_at=datetime(2026, 10, 31, tzinfo=UTC),
        expires_at=datetime(2026, 10, 31, 1, tzinfo=UTC),
        reason=reason,
    )


def _proposing_conversation(*proposals: AgentRunProposal) -> list[dict[str, Any]]:
    """A conversation in which the agent told the clinician the proposals await approval."""
    awaiting = {"status": "awaiting_approval", "proposal_ids": [str(p.id) for p in proposals]}
    return [
        {"role": "user", "content": "Add a task to call her about labs."},
        {
            "role": "assistant",
            "content": [{"type": "tool_use", "id": "t1", "name": "create_task", "input": {}}],
        },
        {
            "role": "user",
            "content": [
                {"type": "tool_result", "tool_use_id": "t1", "content": json.dumps(awaiting)}
            ],
        },
        {"role": "assistant", "content": [{"type": "text", "text": "It awaits your approval."}]},
    ]


def _start(agent: AgentPlugin, messages: list[dict[str, Any]]) -> None:
    state = agent.load_state("patient_and_staff")
    state.data["messages"] = messages
    agent.save_state("patient_and_staff", state)


@pytest.mark.django_db
def test_an_approval_is_recorded_in_the_conversation_before_the_next_message() -> None:
    """The next run writes the outcome into the stored conversation, ahead of the question."""
    patient, staff = PatientFactory.create(), StaffFactory.create()
    approved = _proposal(staff, AgentRunProposalStatus.APPROVED)
    agent = _agent_for(patient.id, staff.id)
    _start(agent, _proposing_conversation(approved))

    run_agent(agent, FakeGateway(reply(text("Done."))), {"user_message": "Anything else?"})

    note, question = load_conversation_messages(patient.id, staff.id)[4:6]
    assert question == {"role": "user", "content": "Anything else?"}
    assert note["role"] == "user"
    assert note["content"][0]["text"] == (
        f"{DECISIONS_NOTE_PREFIX}\n"
        f"- proposal {approved.id} (create_task): approved by the clinician and applied"
    )


@pytest.mark.django_db
def test_the_model_hears_of_a_denial_before_the_next_message_and_only_once() -> None:
    """A denial and its reason reach the model; a pending proposal is left until decided."""
    patient, staff = PatientFactory.create(), StaffFactory.create()
    denied = _proposal(staff, AgentRunProposalStatus.DENIED, reason="Already called her")
    pending = _proposal(staff, AgentRunProposalStatus.PENDING)
    agent = _agent_for(patient.id, staff.id)
    _start(agent, _proposing_conversation(denied, pending))
    gateway = FakeGateway(reply(text("Understood.")), reply(text("Sure.")))

    run_agent(agent, gateway, {"user_message": "OK, what next?"})
    run_agent(_agent_for(patient.id, staff.id), gateway, {"user_message": "Thanks."})

    first, second = (request["messages"] for request in gateway.requests)
    note, question = first[-2:]
    assert note["content"][0]["text"] == (
        f"{DECISIONS_NOTE_PREFIX}\n"
        f"- proposal {denied.id} (create_task): denied by the clinician; nothing changed. "
        "Reason: Already called her"
    )
    assert str(pending.id) not in note["content"][0]["text"]
    assert question == {"role": "user", "content": "OK, what next?"}
    notes = [
        m
        for m in second
        if m["role"] == "user"
        and isinstance(m["content"], list)
        and m["content"][0].get("text", "").startswith(DECISIONS_NOTE_PREFIX)
    ]
    assert len(notes) == 1


@pytest.mark.django_db
def test_another_clinicians_decision_is_not_recorded() -> None:
    """Only the proposals made for this clinician are looked up."""
    patient, staff = PatientFactory.create(), StaffFactory.create()
    theirs = _proposal(StaffFactory.create(), AgentRunProposalStatus.APPROVED)
    agent = _agent_for(patient.id, staff.id)
    _start(agent, _proposing_conversation(theirs))

    gateway = FakeGateway(reply(text("Sure.")))

    run_agent(agent, gateway, {"user_message": "Anything else?"})

    assert gateway.requests[0]["messages"][-1] == {"role": "user", "content": "Anything else?"}
    assert gateway.requests[0]["messages"][-2]["role"] == "assistant"
