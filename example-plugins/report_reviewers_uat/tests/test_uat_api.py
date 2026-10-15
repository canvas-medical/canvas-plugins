import json
from base64 import b64encode
from http import HTTPStatus
from typing import Any

import pytest
from report_reviewers_uat.handlers.uat_api import ReportReviewersUatAPI

from canvas_sdk.effects import Effect
from canvas_sdk.effects.simple_api import Response
from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.test_utils.factories import (
    ImagingReportFactory,
    LabReportFactory,
    PatientAdministrativeDocumentFactory,
    StaffFactory,
    TeamFactory,
)
from canvas_sdk.v1.data import Staff


def _call(
    endpoint: str,
    query_string: str = "",
    logged_in_staff: Staff | None = None,
) -> tuple[HTTPStatus, dict[str, Any]]:
    """Call a GET endpoint of the UAT API and return its status and decoded JSON body."""
    headers = {"canvas-logged-in-user-type": "Staff"}
    if logged_in_staff is not None:
        headers["canvas-logged-in-user-id"] = str(logged_in_staff.id)
    event = Event(
        EventRequest(
            type=EventType.SIMPLE_API_REQUEST,
            context=json.dumps(
                {
                    "method": "GET",
                    "path": f"/{endpoint}",
                    "query_string": query_string,
                    "body": b64encode(b"").decode(),
                    "headers": headers,
                }
            ),
        )
    )
    result: list[Response | Effect] = getattr(ReportReviewersUatAPI(event), endpoint)()
    response = result[0]
    assert isinstance(response, Response)
    return HTTPStatus(response.status_code), json.loads(response.content or b"{}")


@pytest.mark.django_db
def test_run_passes_and_samples_assigned_documents() -> None:
    """/run reports every type as passing and samples the documents that have reviewers."""
    reviewer = StaffFactory.create()
    report = LabReportFactory.create()
    report.reviewers.add(reviewer)
    LabReportFactory.create()

    status, body = _call("run")

    assert status == HTTPStatus.OK
    assert body["all_passed"] is True
    lab = body["results"]["lab_report"]
    assert (lab["total"], lab["assigned"]) == (2, 1)
    assert [document["id"] for document in lab["sample"]] == [str(report.id)]
    assert lab["sample"][0]["reviewers"] == [
        {"id": str(reviewer.id), "name": f"{reviewer.first_name} {reviewer.last_name}"}
    ]
    assert "lab_report" not in body["types_without_assigned_documents"]
    assert "imaging_report" in body["types_without_assigned_documents"]


@pytest.mark.django_db
def test_queue_defaults_to_the_logged_in_staff_member() -> None:
    """/queue lists only the documents assigned to the logged-in staff member."""
    me, colleague = StaffFactory.create(), StaffFactory.create()
    mine = ImagingReportFactory.create()
    mine.reviewers.add(me)
    ImagingReportFactory.create().reviewers.add(colleague)

    status, body = _call("queue", logged_in_staff=me)

    assert status == HTTPStatus.OK
    assert body["staff"]["id"] == str(me.id)
    assert [document["id"] for document in body["queue"]["imaging_report"]] == [str(mine.id)]
    assert body["queue"]["lab_report"] == []


@pytest.mark.django_db
def test_queue_accepts_a_staff_id_and_rejects_an_unknown_one() -> None:
    """/queue looks up the staff_id query parameter and 404s when it matches no one."""
    colleague = StaffFactory.create()
    report = LabReportFactory.create()
    report.reviewers.add(colleague)

    status, body = _call("queue", f"staff_id={colleague.id}")
    assert status == HTTPStatus.OK
    assert [document["id"] for document in body["queue"]["lab_report"]] == [str(report.id)]

    status, _ = _call("queue", "staff_id=00000000000000000000000000000000")
    assert status == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_document_returns_its_reviewers() -> None:
    """/document returns the reviewers of the requested document."""
    reviewer = StaffFactory.create()
    report = LabReportFactory.create()
    report.reviewers.add(reviewer)

    status, body = _call("document", f"type=lab_report&id={report.id}")

    assert status == HTTPStatus.OK
    assert body["id"] == str(report.id)
    assert [staff["id"] for staff in body["reviewers"]] == [str(reviewer.id)]


@pytest.mark.django_db
def test_document_rejects_unknown_type_and_missing_document() -> None:
    """/document 400s on an unknown type and 404s on a document that does not exist."""
    status, _ = _call("document", "type=invoice&id=x")
    assert status == HTTPStatus.BAD_REQUEST

    status, _ = _call("document", "type=lab_report&id=00000000-0000-0000-0000-000000000000")
    assert status == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_document_returns_the_assigned_team() -> None:
    """/document returns the team a lab report is assigned to, with no individual reviewers."""
    team = TeamFactory.create()
    report = LabReportFactory.create(team=team)

    status, body = _call("document", f"type=lab_report&id={report.id}")

    assert status == HTTPStatus.OK
    assert body["team"] == {"id": str(team.id), "name": team.name}
    assert body["reviewers"] == []


@pytest.mark.django_db
def test_document_reads_a_patient_administrative_document() -> None:
    """/document reads a patient administrative document, which has no review relation."""
    reviewer = StaffFactory.create()
    document = PatientAdministrativeDocumentFactory.create()
    document.reviewers.add(reviewer)

    status, body = _call("document", f"type=patient_administrative_document&id={document.id}")

    assert status == HTTPStatus.OK
    assert body["reviewed"] is None
    assert body["team"] is None
    assert [staff["id"] for staff in body["reviewers"]] == [str(reviewer.id)]
