import json
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest
from canvas__agent_runner_poc.agents.claims_chat import (
    NO_REVENUE_ACCESS,
    ClaimsChatAgent,
    _save_claims_conversation,
    load_claims_conversation,
)
from canvas__agent_runner_poc.agents.decisions import note_prefix
from canvas__agent_runner_poc.models.claim_conversation import ClaimConversation

from canvas_sdk.agents import AgentPlugin, Capability, RunRequester, RunSubject
from canvas_sdk.effects import EffectType
from canvas_sdk.test_utils.agents import (
    FakeGateway,
    prepare_agent,
    reply,
    run_agent,
    text,
    tool_use,
)
from canvas_sdk.test_utils.factories import ClaimFactory, ClaimQueueFactory, StaffFactory
from canvas_sdk.v1.data import AgentRun, AgentRunProposal, AgentRunProposalStatus, AgentRunStatus

GRANT = ["@claims_reads", "@claims_writes"]


def _agent(staff_id: str, claim_id: str | None = None, *, revenue: bool = True) -> AgentPlugin:
    """The claims chat as the platform sets it up for one staff member's run."""
    return prepare_agent(
        ClaimsChatAgent,
        allowed=GRANT,
        subject=RunSubject(claim_id=claim_id),
        requester=RunRequester(staff_id=staff_id),
        capabilities=[Capability.REVENUE] if revenue else [],
    )


@pytest.mark.django_db
def test_the_queue_and_each_claim_have_their_own_conversation() -> None:
    """A claim's chat never becomes the queue chat's context, or another claim's."""
    staff_id = StaffFactory.create().id
    claim = ClaimFactory.create()
    queue_chat = _agent(staff_id)

    state = queue_chat.load_state("staff")
    state.data["messages"] = [{"role": "user", "content": "What is in coding review?"}]
    queue_chat.save_state("staff", state)

    assert _agent(staff_id, str(claim.id)).load_state("claim").data["messages"] == []
    assert load_claims_conversation(staff_id, None) == [
        {"role": "user", "content": "What is in coding review?"}
    ]


@pytest.mark.django_db
def test_a_staff_member_without_revenue_access_is_told_so_without_a_model_call() -> None:
    """The agent checks the capability the platform granted before spending a model call."""
    staff_id = StaffFactory.create().id

    run = run_agent(_agent(staff_id, revenue=False), FakeGateway(), {"user_message": "hi"})

    assert run.model_calls == 0
    assert load_claims_conversation(staff_id, None)[-1] == {
        "role": "assistant",
        "content": NO_REVENUE_ACCESS,
    }


@pytest.mark.django_db
def test_a_claim_chat_reads_and_works_the_claim_it_was_opened_from() -> None:
    """Tools default to the run's claim, and a write comes back as an effect to apply."""
    staff_id = StaffFactory.create().id
    claim = ClaimFactory.create()
    gateway = FakeGateway(
        reply(tool_use("get_claim")),
        reply(tool_use("add_claim_comment", {"comment": "Called the payer."})),
        reply(text("Added the comment.")),
    )

    run = run_agent(
        _agent(staff_id, str(claim.id)), gateway, {"user_message": "Note that I called the payer."}
    )

    assert [(call.name, call.ok) for call in run.tool_calls] == [
        ("get_claim", True),
        ("add_claim_comment", True),
    ]
    (effect,) = run.effects
    assert effect.type == EffectType.ADD_CLAIM_COMMENT
    assert json.loads(effect.payload)["data"]["claim_id"] == str(claim.id)
    assert str(claim.id) in gateway.requests[0]["system"][0]["text"]
    saved = load_claims_conversation(staff_id, str(claim.id))
    assert saved[-1]["content"][0]["text"] == "Added the comment."


@pytest.mark.django_db
def test_the_queue_chat_finds_claims_across_patients() -> None:
    """Queue mode has no claim, so the model searches the queues."""
    staff_id = StaffFactory.create().id
    queue = ClaimQueueFactory.create(queue_sort_ordering=3, name="NeedsCodingReview")
    ClaimFactory.create(current_queue=queue)
    ClaimFactory.create(current_queue=queue)
    gateway = FakeGateway(
        reply(tool_use("find_claims", {"queue": "NeedsCodingReview"})),
        reply(text("Two claims are waiting on coding review.")),
    )

    run = run_agent(_agent(staff_id), gateway, {"user_message": "What needs coding review?"})

    assert [(call.name, call.ok) for call in run.tool_calls] == [("find_claims", True)]
    tool_result = gateway.requests[1]["messages"][-1]["content"][0]["content"]
    assert len(json.loads(tool_result)) == 2
    assert "claims queues" in gateway.requests[0]["system"][0]["text"]


def _claims_proposal(staff: Any, status: str) -> AgentRunProposal:
    """A claim move the claims chat proposed for ``staff``, decided as ``status``."""
    run = AgentRun.objects.create(
        id=uuid4(),
        plugin_name="canvas__agent_runner_poc",
        agent_id="canvas__agent_runner_poc.agents.claims_chat:ClaimsChatAgent",
        handler_name="canvas__agent_runner_poc.applications.claims_chat:ClaimsChatAPI",
        scope="staff",
        scope_key="k",
        staff=staff,
        status=AgentRunStatus.SUCCEEDED,
        error_kind="",
        error="",
        queued_at=datetime(2026, 10, 31, tzinfo=UTC),
        attempts=0,
        stop_reason="",
        capabilities=["revenue"],
    )
    return AgentRunProposal.objects.create(
        id=uuid4(),
        run=run,
        plugin_name="canvas__agent_runner_poc",
        agent_id="canvas__agent_runner_poc.agents.claims_chat:ClaimsChatAgent",
        tool="move_claim_to_queue",
        arguments={"claim_id": "c1", "queue": "Coding review"},
        effect_types=["MOVE_CLAIM_TO_QUEUE"],
        staff=staff,
        status=status,
        created_at=datetime(2026, 10, 31, tzinfo=UTC),
        expires_at=datetime(2026, 10, 31, 1, tzinfo=UTC),
        reason="",
    )


@pytest.mark.django_db
def test_a_claim_write_is_proposed_and_its_decision_heard_on_the_next_run() -> None:
    """A move waits for the staff member, and the model learns what they decided."""
    staff = StaffFactory.create()
    agent = _agent(staff.id)
    approved = _claims_proposal(staff, AgentRunProposalStatus.APPROVED)
    awaiting = {"status": "awaiting_approval", "proposal_ids": [str(approved.id)]}
    state = agent.load_state("staff")
    state.data["messages"] = [
        {"role": "user", "content": "Move it to coding review."},
        {
            "role": "assistant",
            "content": [
                {"type": "tool_use", "id": "t1", "name": "move_claim_to_queue", "input": {}}
            ],
        },
        {
            "role": "user",
            "content": [
                {"type": "tool_result", "tool_use_id": "t1", "content": json.dumps(awaiting)}
            ],
        },
        {"role": "assistant", "content": [{"type": "text", "text": "It awaits your approval."}]},
    ]
    agent.save_state("staff", state)
    gateway = FakeGateway(reply(text("Done.")))

    run_agent(agent, gateway, {"user_message": "Anything else?"})

    note = gateway.requests[0]["messages"][-2]
    assert note["content"][0]["text"] == (
        f"{note_prefix('staff member')}\n"
        f"- proposal {approved.id} (move_claim_to_queue): approved by the staff member and "
        "applied"
    )


@pytest.mark.django_db
@pytest.mark.parametrize("claim", [None, str(uuid4())], ids=["queues", "claim"])
def test_saving_a_claims_conversation_again_updates_its_one_row(claim: str | None) -> None:
    """One conversation per staff member and claim, or about the queues."""
    staff = StaffFactory.create()

    _save_claims_conversation(staff.id, claim, [{"role": "user", "content": "first"}])
    _save_claims_conversation(staff.id, claim, [{"role": "user", "content": "second"}])

    (row,) = ClaimConversation.objects.filter(staff__id=staff.id, claim_id=claim or "")
    assert row.messages == [{"role": "user", "content": "second"}]
