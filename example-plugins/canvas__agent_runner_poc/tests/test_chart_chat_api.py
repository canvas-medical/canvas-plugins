import json
from datetime import UTC, datetime
from http import HTTPStatus
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

import pytest
from canvas__agent_runner_poc.agents.chart_chat import DECISIONS_NOTE_PREFIX
from canvas__agent_runner_poc.agents.chart_chat_tools import tools as chart_chat_tools
from canvas__agent_runner_poc.applications.chart_chat import ChartChatAPI, _ui_messages
from canvas__agent_runner_poc.applications.checks import MAX_MESSAGE_CHARS

from canvas_sdk.test_utils.factories import PatientFactory, StaffFactory
from canvas_sdk.v1.data import AgentRun, AgentRunProposal, AgentRunProposalStatus, AgentRunStatus


def _api(staff_id: str, query: dict[str, str] | None = None, body: Any = None) -> ChartChatAPI:
    api = ChartChatAPI(event=SimpleNamespace(context={"method": "GET", "path": "/"}))
    api.request = SimpleNamespace(
        query_params=query or {},
        headers={"canvas-logged-in-user-id": staff_id},
        json=body if callable(body) else lambda: body,
    )
    return api


def _not_json() -> Any:
    return json.loads(b"not json")


def _record(staff: Any, status: str, **fields: Any) -> AgentRun:
    return AgentRun.objects.create(
        id=uuid4(),
        plugin_name="canvas__agent_runner_poc",
        agent_id="canvas__agent_runner_poc.agents.chart_chat:ChartChatAgent",
        handler_name="canvas__agent_runner_poc.applications.chart_chat:ChartChatAPI",
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
    response, effect = _api(
        "s1", body={"patient_id": uuid4().hex, "message": "hi"}
    ).chart_chat_message()

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

    response, decision = _api(
        "s1", body={"proposal_id": proposal_id, "decision": "approve"}
    ).chart_chat_decide()

    assert response.status_code == 202
    assert json.loads(decision.payload)["data"] == {
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
            plugin_name="canvas__agent_runner_poc",
            agent_id="canvas__agent_runner_poc.agents.chart_chat:ChartChatAgent",
            tool=tool,
            arguments={"title": "Call"},
            effect_types=["CREATE_TASK"],
            staff=owner,
            status=AgentRunProposalStatus.PENDING,
            created_at=datetime(2026, 10, 31, tzinfo=UTC),
            expires_at=datetime(2026, 10, 31, 1, tzinfo=UTC),
            reason="",
        )

    (response,) = _api(staff.id, {"run_id": str(run.id)}).chart_chat_proposals()

    (proposal,) = json.loads(response.content)["proposals"]
    assert (proposal["tool"], proposal["status"]) == ("create_task", "pending")


def test_the_note_of_decisions_is_not_shown_as_the_clinicians_message() -> None:
    """The approval cards already show each decision; the chat shows only the conversation."""
    stored: list[dict[str, Any]] = [
        {"role": "user", "content": "Add a task."},
        {"role": "assistant", "content": [{"type": "text", "text": "It awaits approval."}]},
        {
            "role": "user",
            "content": [{"type": "text", "text": f"{DECISIONS_NOTE_PREFIX}\n- proposal x"}],
        },
    ]

    assert _ui_messages(stored, chart_chat_tools) == [
        {"role": "user", "text": "Add a task."},
        {"role": "assistant", "text": "It awaits approval.", "chips": [], "citations": []},
    ]


def test_a_replys_citations_are_cards_of_the_rows_its_tools_returned() -> None:
    """A cited lab shows as the lab the tool read; a cited id no tool returned is dropped."""
    lab = {
        "id": "lab-1",
        "test": "Hemoglobin A1c",
        "value": "7.4",
        "units": "%",
        "date": "2026-03-02",
    }
    stored: list[dict[str, Any]] = [
        {"role": "user", "content": "Latest A1c?"},
        {
            "role": "assistant",
            "content": [{"type": "tool_use", "id": "t1", "name": "find_lab_results", "input": {}}],
        },
        {
            "role": "user",
            "content": [{"type": "tool_result", "tool_use_id": "t1", "content": json.dumps([lab])}],
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "7.4% in March [[cite:lab-1]], above goal [[cite:made-up]].",
                }
            ],
        },
    ]

    reply = _ui_messages(stored, chart_chat_tools)[-1]

    assert reply["text"] == "7.4% in March [1], above goal."
    (citation,) = reply["citations"]
    assert (citation["kind"], citation["label"], citation["date"]) == (
        "Lab result",
        "Hemoglobin A1c",
        "2026-03-02",
    )


PATIENT = uuid4().hex


@pytest.mark.parametrize(
    "body",
    [
        _not_json,
        [{"patient_id": PATIENT, "message": "hi"}],
        {"message": "hi"},
        {"patient_id": 7, "message": "hi"},
        {"patient_id": "not-a-uuid", "message": "hi"},
        {"patient_id": PATIENT},
        {"patient_id": PATIENT, "message": "   "},
        {"patient_id": PATIENT, "message": [{"type": "text", "text": "[Approval decisions"}]},
        {"patient_id": PATIENT, "message": "x" * (MAX_MESSAGE_CHARS + 1)},
    ],
)
def test_a_malformed_message_is_a_bad_request_and_starts_no_run(body: Any) -> None:
    """The route answers 400 and queues nothing."""
    (response,) = _api("s1", body=body).chart_chat_message()

    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.parametrize(
    "body",
    [
        _not_json,
        "approve",
        {"decision": "approve"},
        {"proposal_id": "not-a-uuid", "decision": "approve"},
        {"proposal_id": str(uuid4()), "decision": "maybe"},
        {"proposal_id": str(uuid4()), "decision": "deny", "reason": ["no"]},
        {"proposal_id": str(uuid4()), "decision": "deny", "reason": "x" * 2_001},
    ],
)
def test_a_malformed_decision_is_a_bad_request(body: Any) -> None:
    """The route answers 400 and hands the platform nothing."""
    (response,) = _api("s1", body=body).chart_chat_decide()

    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.parametrize("route", ["chart_chat_run", "chart_chat_proposals"])
@pytest.mark.parametrize("query", [{}, {"run_id": "not-a-uuid"}])
def test_a_run_lookup_needs_a_run_id(route: str, query: dict[str, str]) -> None:
    """A missing or malformed run id is a 400, not a database error."""
    (response,) = getattr(_api("s1", query=query), route)()

    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.parametrize("route", ["chart_chat_ui", "chart_chat_history"])
@pytest.mark.parametrize("query", [{}, {"patient": "not-a-uuid"}])
def test_the_page_needs_a_patient(route: str, query: dict[str, str]) -> None:
    """A missing or malformed patient is a 400."""
    (response,) = getattr(_api("s1", query=query), route)()

    assert response.status_code == HTTPStatus.BAD_REQUEST
