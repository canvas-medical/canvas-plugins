import json
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

import pytest
from agent_runner_poc.applications.chart_chat import ChartChatAPI

from canvas_sdk.test_utils.factories import PatientFactory, StaffFactory
from canvas_sdk.v1.data import AgentRun, AgentRunProposal, AgentRunProposalStatus, AgentRunStatus


def _api(staff_id: str, query: dict[str, str] | None = None, body: Any = None) -> ChartChatAPI:
    api = ChartChatAPI(event=SimpleNamespace(context={"method": "GET", "path": "/"}))
    api.request = SimpleNamespace(
        query_params=query or {},
        headers={"canvas-logged-in-user-id": staff_id},
        json=lambda: body,
    )
    return api


def _record(staff: Any, status: str, **fields: Any) -> AgentRun:
    return AgentRun.objects.create(
        id=uuid4(),
        plugin_name="agent_runner_poc",
        agent_id="agent_runner_poc.agents.chart_chat:ChartChatAgent",
        handler_name="agent_runner_poc.applications.chart_chat:ChartChatAPI",
        scope="patient_and_staff",
        scope_key="k",
        staff=staff,
        status=status,
        error_kind=fields.pop("error_kind", ""),
        error="",
        queued_at=datetime(2026, 10, 29, tzinfo=UTC),
        attempts=0,
        stop_reason="",
        capabilities=[],
        **fields,
    )


def test_a_message_returns_the_run_id_its_run_carries() -> None:
    """The UI polls the run with the id the effect generated."""
    response, effect = _api("s1", body={"patient_id": "p1", "message": "hi"}).chart_chat_message()

    returned = json.loads(response.content)
    assert returned["status"] == "queued"
    assert returned["run_id"] == json.loads(effect.payload)["data"]["run_id"]


@pytest.mark.django_db
def test_the_clinician_sees_their_runs_status() -> None:
    """A failed run reports its kind so the UI can say what went wrong."""
    staff = StaffFactory.create()
    run = _record(staff, AgentRunStatus.FAILED, error_kind="LLM_REFUSED")

    (response,) = _api(staff.id, {"run_id": str(run.id)}).chart_chat_run()

    assert json.loads(response.content) == {"status": "failed", "error_kind": "LLM_REFUSED"}


@pytest.mark.django_db
def test_another_clinicians_run_is_not_revealed() -> None:
    """A run id from someone else's chat reads like a run not recorded yet."""
    run = _record(StaffFactory.create(), AgentRunStatus.SUCCEEDED, patient=PatientFactory.create())

    (response,) = _api(StaffFactory.create().id, {"run_id": str(run.id)}).chart_chat_run()

    assert json.loads(response.content) == {"status": "queued", "error_kind": ""}


def test_a_decision_goes_to_the_platform_as_the_clinicians() -> None:
    """The plugin hands the decision over; the platform checks it is the requester's."""
    proposal_id = str(uuid4())

    response, effect = _api(
        "s1", body={"proposal_id": proposal_id, "decision": "approve"}
    ).chart_chat_decide()

    assert response.status_code == 202
    assert json.loads(effect.payload)["data"] == {
        "proposal_id": proposal_id,
        "decision": "approve",
        "reason": "",
    }


@pytest.mark.django_db
def test_a_run_shows_only_the_clinicians_own_proposals() -> None:
    """Another clinician's proposal on the same run id is not offered for approval."""
    staff, other = StaffFactory.create(), StaffFactory.create()
    run = _record(staff, AgentRunStatus.SUCCEEDED)
    for owner, tool in ((staff, "create_task"), (other, "add_banner_alert")):
        AgentRunProposal.objects.create(
            id=uuid4(),
            run=run,
            plugin_name="agent_runner_poc",
            agent_id="agent_runner_poc.agents.chart_chat:ChartChatAgent",
            tool=tool,
            arguments={"title": "Call"},
            effect_type="CREATE_TASK",
            staff=owner,
            status=AgentRunProposalStatus.PENDING,
            created_at=datetime(2026, 10, 31, tzinfo=UTC),
            expires_at=datetime(2026, 10, 31, 1, tzinfo=UTC),
            reason="",
        )

    (response,) = _api(staff.id, {"run_id": str(run.id)}).chart_chat_proposals()

    (proposal,) = json.loads(response.content)["proposals"]
    assert (proposal["tool"], proposal["status"]) == ("create_task", "pending")
