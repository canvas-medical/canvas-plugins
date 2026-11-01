"""find_documents: a patient's consult notes and outside records, described from the chart."""

import json
from datetime import date
from typing import Any

import pytest

from canvas_sdk.agents import standard_tools
from canvas_sdk.agents.citations import Sources, cite
from canvas_sdk.test_utils.factories import (
    DocumentCodingFactory,
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


def _consult_note(patient: Any, **fields: Any) -> Any:
    fields.setdefault("review", None)
    return ReferralReportFactory.create(patient=patient, referral=None, **fields)


def _outside_record(patient: Any, **fields: Any) -> Any:
    fields.setdefault("review", None)
    return UncategorizedClinicalDocumentFactory.create(patient=patient, **fields)


@pytest.mark.django_db
def test_a_consult_note_carries_its_specialty_values_comment_and_referral() -> None:
    """What staff entered when filing the note is what the agent can quote."""
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
        comment="Recommends a Holter monitor.",
    )
    ReferralReportCodingFactory.create(report=report, display="Impression", value="Benign PVCs")

    (document,) = _documents(patient)

    assert document["id"] == str(report.id)
    assert (document["type"], document["name"], document["from"]) == (
        "Consult note",
        "Cardiology",
        "Heart Partners",
    )
    assert (document["date"], document["review"]) == ("2026-09-14", "reviewed")
    assert document["comment"] == "Recommends a Holter monitor."
    assert document["values"] == [{"name": "Impression", "value": "Benign PVCs"}]
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
def test_documents_are_the_patients_own_and_not_junked() -> None:
    """Another patient's note, and a document filed as junk, never appear."""
    patient = PatientFactory.create()
    _consult_note(patient, specialty="Neurology")
    _consult_note(patient, specialty="Junked", junked=True)
    _consult_note(PatientFactory.create(), specialty="Someone else's")
    _outside_record(patient, name="Junk fax", junked=True)
    _outside_record(PatientFactory.create(), name="Someone else's record")

    assert [document["name"] for document in _documents(patient)] == ["Neurology"]


@pytest.mark.django_db
def test_the_kind_name_and_date_filters_narrow_the_list() -> None:
    """'The cardiology note', 'outside records', and 'since June' each narrow it."""
    patient = PatientFactory.create()
    _consult_note(patient, specialty="Cardiology", original_date=date(2026, 9, 1))
    _consult_note(patient, specialty="Dermatology", original_date=date(2026, 3, 1))
    _outside_record(patient, name="Echo report", original_date=date(2026, 7, 1))

    assert [d["name"] for d in _documents(patient, kind="outside_record")] == ["Echo report"]
    assert [d["name"] for d in _documents(patient, name_contains="cardio")] == ["Cardiology"]
    assert [d["name"] for d in _documents(patient, dated_on_or_after="2026-06-01")] == [
        "Cardiology",
        "Echo report",
    ]


@pytest.mark.django_db
def test_unreviewed_only_finds_documents_waiting_past_newer_reviewed_ones() -> None:
    """The review filter runs before the limit, so an older unreviewed note is not crowded out."""
    patient = PatientFactory.create()
    for day in range(1, 4):
        _consult_note(
            patient,
            specialty=f"Reviewed {day}",
            original_date=date(2026, 9, day + 10),
            review=ReferralReviewFactory.create(
                patient=patient, status=ReviewStatus.STATUS_REVIEWED
            ),
        )
    _consult_note(patient, specialty="Waiting", original_date=date(2026, 9, 1))
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
def test_long_comments_and_values_are_clipped() -> None:
    """A pasted-in report does not flood the model's context."""
    patient = PatientFactory.create()
    report = _consult_note(patient, comment="x" * 2000)
    ReferralReportCodingFactory.create(report=report, display="Findings", value="y" * 900)

    (document,) = _documents(patient)

    assert len(document["comment"]) == 500
    assert len(document["values"][0]["value"]) == 300


@pytest.mark.django_db
def test_a_cited_document_is_described_from_its_row() -> None:
    """The source card names the document, its kind, and its review status."""
    patient = PatientFactory.create()
    report = _consult_note(patient, specialty="Cardiology", original_date=date(2026, 9, 14))
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
        "Consult note",
        "Cardiology",
        "not reviewed",
        "2026-09-14",
    )
