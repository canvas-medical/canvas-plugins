import json
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

import pytest
from canvas__agent_runner_poc.agents.claims_chat import _save_claims_conversation
from canvas__agent_runner_poc.applications.claims_chat import CLAIMS_CHAT_AGENT_ID, ClaimsChatAPI

from canvas_sdk.test_utils.factories import StaffFactory
from canvas_sdk.v1.data import AgentRun, AgentRunProposal, AgentRunProposalStatus, AgentRunStatus


def _api(staff_id: str, query: dict[str, str] | None = None, body: Any = None) -> ClaimsChatAPI:
    api = ClaimsChatAPI(event=SimpleNamespace(context={"method": "GET", "path": "/"}))
    api.request = SimpleNamespace(
        query_params=query or {},
        headers={"canvas-logged-in-user-id": staff_id},
        json=lambda: body,
    )
    return api


def _run_data(effect: Any) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(effect.payload)["data"]
    return data


def test_a_message_without_a_claim_runs_on_the_staff_members_queue_conversation() -> None:
    """Queue mode serializes one staff member's runs and names no claim."""
    response, effect = _api("s1", body={"message": "hi"}).claims_chat_message()

    data = _run_data(effect)
    assert (data["scope"], data["claim_id"]) == ("staff", None)
    assert json.loads(response.content)["run_id"] == data["run_id"]


def test_a_message_about_a_claim_runs_on_that_claim() -> None:
    """Claim mode hands the platform the claim to check and key the run on."""
    claim_id = str(uuid4())

    _, effect = _api("s1", body={"claim_id": claim_id, "message": "hi"}).claims_chat_message()

    data = _run_data(effect)
    assert (data["scope"], data["claim_id"]) == ("claim", claim_id)


@pytest.mark.django_db
def test_a_refused_run_reports_the_platforms_reason() -> None:
    """A staff member without revenue access learns why the claim chat did not start."""
    staff = StaffFactory.create()
    run = AgentRun.objects.create(
        id=uuid4(),
        plugin_name="canvas__agent_runner_poc",
        agent_id=CLAIMS_CHAT_AGENT_ID,
        handler_name="canvas__agent_runner_poc.applications.claims_chat:ClaimsChatAPI",
        scope="claim",
        scope_key="",
        staff=staff,
        status=AgentRunStatus.REFUSED,
        error_kind="",
        error="Only a staff member with revenue access to every patient can start an agent run about a claim.",
        queued_at=datetime(2026, 10, 31, tzinfo=UTC),
        attempts=0,
        stop_reason="",
        capabilities=[],
    )

    (response,) = _api(staff.id, {"run_id": str(run.id)}).claims_chat_run()

    body = json.loads(response.content)
    assert body["status"] == "refused"
    assert "revenue access" in body["error"]


@pytest.mark.django_db
def test_history_is_the_conversation_for_the_page_mode() -> None:
    """The claim page shows the claim's conversation; the queue page shows the queue's."""
    staff = StaffFactory.create()
    claim_id = str(uuid4())
    _save_claims_conversation(staff.id, claim_id, [{"role": "user", "content": "about the claim"}])

    (claim_page,) = _api(staff.id, {"claim": claim_id}).claims_chat_history()
    (queue_page,) = _api(staff.id).claims_chat_history()

    assert json.loads(claim_page.content)["messages"] == [
        {"role": "user", "text": "about the claim"}
    ]
    assert json.loads(queue_page.content)["messages"] == []


def test_a_decision_goes_to_the_platform_as_the_staff_members() -> None:
    """The plugin hands the decision over; the platform checks it is the requester's."""
    proposal_id = str(uuid4())

    response, decision = _api(
        "s1", body={"proposal_id": proposal_id, "decision": "deny"}
    ).claims_chat_decide()

    assert response.status_code == 202
    assert json.loads(decision.payload)["data"] == {
        "proposal_id": proposal_id,
        "decision": "deny",
        "reason": "",
    }


@pytest.mark.django_db
def test_a_run_shows_only_the_staff_members_own_proposals() -> None:
    """Another staff member's proposal on the same run is not offered for approval."""
    staff, other = StaffFactory.create(), StaffFactory.create()
    run = AgentRun.objects.create(
        id=uuid4(),
        plugin_name="canvas__agent_runner_poc",
        agent_id=CLAIMS_CHAT_AGENT_ID,
        handler_name="canvas__agent_runner_poc.applications.claims_chat:ClaimsChatAPI",
        scope="staff",
        scope_key="",
        staff=staff,
        status=AgentRunStatus.SUCCEEDED,
        error_kind="",
        error="",
        queued_at=datetime(2026, 10, 31, tzinfo=UTC),
        attempts=0,
        stop_reason="",
        capabilities=[],
    )
    for owner, tool in ((staff, "move_claim_to_queue"), (other, "unassign_claim")):
        AgentRunProposal.objects.create(
            id=uuid4(),
            run=run,
            plugin_name="canvas__agent_runner_poc",
            agent_id=CLAIMS_CHAT_AGENT_ID,
            tool=tool,
            arguments={"claim_id": "c1"},
            effect_types=["MOVE_CLAIM_TO_QUEUE"],
            staff=owner,
            status=AgentRunProposalStatus.PENDING,
            created_at=datetime(2026, 10, 31, tzinfo=UTC),
            expires_at=datetime(2026, 10, 31, 1, tzinfo=UTC),
            reason="",
        )

    (response,) = _api(staff.id, {"run_id": str(run.id)}).claims_chat_proposals()

    (proposal,) = json.loads(response.content)["proposals"]
    assert (proposal["tool"], proposal["status"]) == ("move_claim_to_queue", "pending")
