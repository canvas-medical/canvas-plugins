import json
from datetime import UTC, datetime
from http import HTTPStatus
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

import pytest
from canvas__agent_runner_poc.agents.claims_chat import _save_claims_conversation
from canvas__agent_runner_poc.applications.checks import MAX_MESSAGE_CHARS
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


@pytest.mark.django_db
def test_the_history_names_the_reply_to_the_newest_message() -> None:
    """The page shows this reply, which a count of replies misses once old turns drop off."""
    staff = StaffFactory.create()
    _save_claims_conversation(
        staff.id,
        None,
        [
            {"role": "assistant", "content": "an older reply"},
            {"role": "user", "content": "the new question"},
            {"role": "assistant", "content": "the new reply"},
        ],
    )

    (response,) = _api(staff.id).claims_chat_history()

    assert json.loads(response.content)["reply"]["text"] == "the new reply"


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


@pytest.mark.parametrize(
    "body",
    [
        ["hi"],
        {"claim_id": "c1", "message": "hi"},
        {"claim_id": 7, "message": "hi"},
        {"message": {"text": "hi"}},
        {"message": "x" * (MAX_MESSAGE_CHARS + 1)},
    ],
)
def test_a_malformed_message_is_a_bad_request_and_starts_no_run(body: Any) -> None:
    """The route answers 400 and queues nothing."""
    (response,) = _api("s1", body=body).claims_chat_message()

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_a_malformed_decision_is_a_bad_request() -> None:
    """The route answers 400 and hands the platform nothing."""
    (response,) = _api("s1", body={"proposal_id": "p1", "decision": "maybe"}).claims_chat_decide()

    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.parametrize(
    ("route", "query"),
    [
        ("claims_chat_run", {}),
        ("claims_chat_proposals", {"run_id": "not-a-uuid"}),
        ("claims_chat_ui", {"claim": "not-a-uuid"}),
        ("claims_chat_history", {"claim": "not-a-uuid"}),
    ],
)
def test_a_malformed_query_is_a_bad_request(route: str, query: dict[str, str]) -> None:
    """A missing or malformed id is a 400, not a database error."""
    (response,) = getattr(_api("s1", query=query), route)()

    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.parametrize("claim", [None, str(uuid4())], ids=["queue mode", "claim mode"])
def test_another_staff_members_conversation_is_not_shown(claim: str | None) -> None:
    """Every biller's queue conversation has no claim, so the staff member is what keeps them apart."""
    owner, colleague = StaffFactory.create(), StaffFactory.create()
    _save_claims_conversation(
        owner.id, claim, [{"role": "user", "content": "claim 4411 for J. Doe"}]
    )

    (response,) = _api(colleague.id, {"claim": claim} if claim else None).claims_chat_history()

    assert json.loads(response.content)["messages"] == []


@pytest.mark.django_db
def test_another_staff_members_run_is_not_revealed() -> None:
    """A run id from someone else's chat reads like a run not recorded yet."""
    run = AgentRun.objects.create(
        id=uuid4(),
        plugin_name="canvas__agent_runner_poc",
        agent_id=CLAIMS_CHAT_AGENT_ID,
        handler_name="canvas__agent_runner_poc.applications.claims_chat:ClaimsChatAPI",
        scope="staff",
        scope_key="",
        staff=StaffFactory.create(),
        status=AgentRunStatus.REFUSED,
        error_kind="",
        error="Only a staff member with revenue access to every patient can start an agent run about a claim.",
        queued_at=datetime(2026, 10, 31, tzinfo=UTC),
        attempts=0,
        stop_reason="",
        capabilities=[],
    )

    (response,) = _api(StaffFactory.create().id, {"run_id": str(run.id)}).claims_chat_run()

    assert json.loads(response.content) == {"status": "queued", "error_kind": "", "error": ""}
