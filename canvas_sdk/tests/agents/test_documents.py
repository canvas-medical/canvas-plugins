"""find_documents: a patient's consult reports and outside records, described from the chart."""

import json
from datetime import date
from typing import Any

import pytest

from canvas_sdk.agents import standard_tools
from canvas_sdk.agents.citations import Sources, cite
from canvas_sdk.test_utils.factories import (
    DocumentCodingFactory,
    IntegrationTaskFactory,
    IntegrationTaskReviewFactory,
    PatientFactory,
    ReferralFactory,
    ReferralReportCodingFactory,
    ReferralReportFactory,
    ReferralReviewFactory,
    ServiceProviderFactory,
    UncategorizedClinicalDocumentFactory,
    UncategorizedClinicalDocumentReviewFactory,
)
from canvas_sdk.v1.data.common import ReviewStatus


def _documents(patient: Any, **arguments: Any) -> list[dict[str, Any]]:
    return standard_tools.execute("find_documents", arguments, ctx={"patient_id": patient.id})


def _consult_report(patient: Any, **fields: Any) -> Any:
    fields.setdefault("review", None)
    return ReferralReportFactory.create(patient=patient, referral=None, **fields)


def _filed_from(file_name: str) -> Any:
    """The review of an incoming fax whose file is ``file_name``."""
    return IntegrationTaskReviewFactory.create(
        task=IntegrationTaskFactory.create(document=file_name)
    )


def _outside_record(patient: Any, **fields: Any) -> Any:
    fields.setdefault("review", None)
    return UncategorizedClinicalDocumentFactory.create(patient=patient, **fields)


@pytest.mark.django_db
def test_a_consult_report_carries_its_specialty_sender_comment_and_file() -> None:
    """Who sent it, when, and the staff's filing comment; what it says is in the fax."""
    patient = PatientFactory.create()
    provider = ServiceProviderFactory.create(first_name="Heart", last_name="Partners")
    referral = ReferralFactory.create(patient=patient, service_provider=provider)
    review_note = ReferralReviewFactory.create(patient=patient, status=ReviewStatus.STATUS_REVIEWED)
    report = ReferralReportFactory.create(
        patient=patient,
        referral=referral,
        review=review_note,
        specialty="Cardiology",
        original_date=date(2026, 9, 14),
        comment="Cardio f/u letter",
        integration_task_review=_filed_from("faxes/cardiology.pdf"),
    )
    # The coding is the specialty's own code, not anything the report says.
    ReferralReportCodingFactory.create(report=report, display="Cardiology", value="207RC")

    (document,) = _documents(patient)

    assert document["id"] == str(report.id)
    assert (document["type"], document["name"], document["from"]) == (
        "Consult report",
        "Cardiology",
        "Heart Partners",
    )
    assert (document["date"], document["review"]) == ("2026-09-14", "reviewed")
    assert document["comment"] == "Cardio f/u letter"
    assert document["has_file"] is True
    assert "values" not in document
    assert document["referral_id"] == str(referral.id)
    assert document["note_dbid"] == review_note.note.dbid


@pytest.mark.django_db
def test_an_outside_record_carries_its_category_comment_and_file() -> None:
    """The record's text is in its file; the row says one is there to read."""
    patient = PatientFactory.create()
    record = _outside_record(
        patient,
        name="Discharge summary",
        code=DocumentCodingFactory.create(display="Hospital records"),
        comment="Admitted for pneumonia.",
        original_date=date(2026, 8, 2),
        document="documents/discharge-summary.pdf",
    )
    _outside_record(patient, name="Phone note", document="", original_date=date(2026, 1, 1))

    document, without_file = _documents(patient)

    assert without_file["has_file"] is False
    assert document["id"] == str(record.id)
    assert (document["type"], document["name"], document["category"]) == (
        "Outside record",
        "Discharge summary",
        "Hospital records",
    )
    assert (document["comment"], document["review"]) == ("Admitted for pneumonia.", "not reviewed")
    assert document["has_file"] is True


@pytest.mark.django_db
def test_a_consult_report_without_a_filed_fax_has_no_file() -> None:
    """A report entered by hand, or filed from a task whose file is gone, has nothing to read."""
    patient = PatientFactory.create()
    _consult_report(patient, specialty="Entered by hand", original_date=date(2026, 9, 2))
    _consult_report(
        patient,
        specialty="Empty task",
        original_date=date(2026, 9, 1),
        integration_task_review=_filed_from(""),
    )

    assert [(d["name"], d["has_file"]) for d in _documents(patient)] == [
        ("Entered by hand", False),
        ("Empty task", False),
    ]


@pytest.mark.django_db
def test_documents_are_the_patients_own_and_not_junked() -> None:
    """Another patient's report, and a document filed as junk, never appear."""
    patient = PatientFactory.create()
    _consult_report(patient, specialty="Neurology")
    _consult_report(patient, specialty="Junked", junked=True)
    _consult_report(PatientFactory.create(), specialty="Someone else's")
    _outside_record(patient, name="Junk fax", junked=True)
    _outside_record(PatientFactory.create(), name="Someone else's record")

    assert [document["name"] for document in _documents(patient)] == ["Neurology"]


@pytest.mark.django_db
def test_the_kind_name_and_date_filters_narrow_the_list() -> None:
    """'The cardiology report', 'outside records', and 'since June' each narrow it."""
    patient = PatientFactory.create()
    _consult_report(patient, specialty="Cardiology", original_date=date(2026, 9, 1))
    _consult_report(patient, specialty="Dermatology", original_date=date(2026, 3, 1))
    _outside_record(patient, name="Echo report", original_date=date(2026, 7, 1))

    assert [d["name"] for d in _documents(patient, kind="outside_record")] == ["Echo report"]
    assert [d["name"] for d in _documents(patient, name_contains="cardio")] == ["Cardiology"]
    assert [d["name"] for d in _documents(patient, dated_on_or_after="2026-06-01")] == [
        "Cardiology",
        "Echo report",
    ]


@pytest.mark.django_db
def test_unreviewed_only_finds_documents_waiting_past_newer_reviewed_ones() -> None:
    """The review filter runs before the limit, so an older unreviewed report is not crowded out."""
    patient = PatientFactory.create()
    for day in range(1, 4):
        _consult_report(
            patient,
            specialty=f"Reviewed {day}",
            original_date=date(2026, 9, day + 10),
            review=ReferralReviewFactory.create(
                patient=patient, status=ReviewStatus.STATUS_REVIEWED
            ),
        )
    _consult_report(patient, specialty="Waiting", original_date=date(2026, 9, 1))
    _outside_record(
        patient,
        name="In review",
        review=UncategorizedClinicalDocumentReviewFactory.create(
            patient=patient, status=ReviewStatus.STATUS_REVIEWING
        ),
    )

    documents = _documents(patient, unreviewed_only=True, limit=2)

    assert {(d["name"], d["review"]) for d in documents} == {
        ("Waiting", "not reviewed"),
        ("In review", "in review"),
    }


@pytest.mark.django_db
def test_a_long_comment_is_clipped() -> None:
    """A pasted-in report does not flood the model's context."""
    patient = PatientFactory.create()
    _consult_report(patient, comment="x" * 2000)

    (document,) = _documents(patient)

    assert len(document["comment"]) == 500


@pytest.mark.django_db
def test_a_cited_document_is_described_from_its_row() -> None:
    """The source card names the document, its kind, and its review status."""
    patient = PatientFactory.create()
    report = _consult_report(patient, specialty="Cardiology", original_date=date(2026, 9, 14))
    rows = _documents(patient)
    sources = Sources(standard_tools).add_all(
        [
            {
                "role": "assistant",
                "content": [{"type": "tool_use", "id": "t1", "name": "find_documents"}],
            },
            {
                "role": "user",
                "content": [
                    {"type": "tool_result", "tool_use_id": "t1", "content": json.dumps(rows)}
                ],
            },
        ]
    )

    _, (citation,) = cite(f"Cardiology wrote back [[cite:{report.id}]].", sources)

    assert (citation.kind, citation.label, citation.detail, citation.date) == (
        "Consult report",
        "Cardiology",
        "not reviewed",
        "2026-09-14",
    )
