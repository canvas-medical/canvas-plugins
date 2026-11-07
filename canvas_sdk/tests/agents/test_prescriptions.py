"""Prescriptions written here, what pharmacies dispensed, and what pharmacies asked."""

import json
from datetime import UTC, datetime
from typing import Any

import pytest

from canvas_sdk.agents import standard_tools
from canvas_sdk.agents.citations import Sources, cite
from canvas_sdk.test_utils.factories import (
    CanvasUserFactory,
    MedicationHistoryMedicationFactory,
    PatientFactory,
    PrescriptionChangeRequestFactory,
    PrescriptionChangeResponseFactory,
    PrescriptionFactory,
    StaffFactory,
)
from canvas_sdk.v1.data import RefillRequest


def _find(tool: str, patient: Any, **arguments: Any) -> Any:
    return standard_tools.execute(tool, arguments, ctx={"patient_id": patient.id})


def _refill_request(patient: Any, reference: str, **fields: Any) -> Any:
    """A pharmacy's request to renew lisinopril, under Rx reference ``reference``."""
    return RefillRequest.objects.create(
        patient=patient,
        message_id=reference,
        content={
            "rx_reference_number": reference,
            "pharmacy": {"name": "Corner Pharmacy"},
            "dispensed_medication": {
                "drug_description": "lisinopril 10 mg tablet",
                "directions": "TAKE 1 TABLET BY MOUTH DAILY",
                "quantity": "30",
                "days_supply": "30",
                "last_fill_date": "2026-09-01",
            },
        },
        **fields,
    )


def _answer(patient: Any, request: Any, response_type: str = "A", **fields: Any) -> Any:
    """A prescriber's committed answer to ``request``."""
    return PrescriptionFactory.create(
        patient=patient,
        committer=CanvasUserFactory.create(),
        refill_request=request,
        response_type=response_type,
        **fields,
    )


@pytest.mark.django_db
def test_a_prescription_says_how_much_was_sent_where_and_by_whom() -> None:
    """Quantity, refills, pharmacy, and prescriber come back with the note it was written in."""
    patient = PatientFactory.create()
    prescriber = StaffFactory.create(first_name="Ada", last_name="Okafor")
    prescription = PrescriptionFactory.create(
        patient=patient,
        prescriber=prescriber,
        committer=CanvasUserFactory.create(),
        status="delivered",
        error_message="stale text from an earlier attempt",
    )

    (row,) = _find("find_prescriptions", patient)

    assert {key: row[key] for key in ("dispense_quantity", "days_supply", "refills")} == {
        "dispense_quantity": 4,
        "days_supply": 22,
        "refills": 1,
    }
    assert (row["pharmacy"], row["prescriber"]) == ("Walgreens", "Ada Okafor")
    assert row["note_dbid"] == prescription.note_id
    # The error message only means something when sending failed.
    assert (row["status"], row["error"], row["response"]) == ("delivered", None, None)


@pytest.mark.django_db
def test_prescriptions_that_never_reached_the_pharmacy_filter_by_status() -> None:
    """The status filter takes the statuses prescriptions really have, such as error."""
    patient = PatientFactory.create()
    committer = CanvasUserFactory.create()
    PrescriptionFactory.create(patient=patient, committer=committer, status="delivered")
    PrescriptionFactory.create(
        patient=patient,
        committer=committer,
        status="error",
        error_message="Pharmacy not found",
    )
    (definition,) = (d for d in standard_tools.definitions() if d["name"] == "find_prescriptions")

    (row,) = _find("find_prescriptions", patient, status="error")

    assert "error" in definition["input_schema"]["properties"]["status"]["enum"]
    assert (row["status"], row["error"]) == ("error", "Pharmacy not found")


@pytest.mark.django_db
def test_a_fill_says_when_the_supply_runs_out_and_who_prescribed_it() -> None:
    """A fill from another prescriber, with the day its supply ends."""
    patient = PatientFactory.create()
    MedicationHistoryMedicationFactory.create(
        patient=patient,
        drug_description="atorvastatin 40 mg tablet",
        last_fill_date=datetime(2026, 9, 10, tzinfo=UTC),
        days_supply=90,
        pharmacy_name="Corner Pharmacy",
        prescriber_first_name="Lee",
        prescriber_last_name="Park",
    )
    MedicationHistoryMedicationFactory.create(patient=PatientFactory.create())

    (fill,) = _find("find_pharmacy_fills", patient, name_contains="atorva")

    assert (fill["drug"], fill["last_fill_date"], fill["supply_ends"]) == (
        "atorvastatin 40 mg tablet",
        "2026-09-10",
        "2026-12-09",
    )
    assert (fill["pharmacy"], fill["prescriber"]) == ("Corner Pharmacy", "Lee Park")
    assert fill["retrieved"]


@pytest.mark.django_db
def test_refill_requests_are_waiting_answered_or_ignored() -> None:
    """An answer settles every resend of its request; an ignored one is set aside."""
    patient = PatientFactory.create()
    waiting = _refill_request(patient, "RX-1")
    first_ask = _refill_request(patient, "RX-2")
    resent = _refill_request(patient, "RX-2")
    ignored = _refill_request(patient, "RX-3", ignored=True)
    answer = _answer(patient, first_ask, response_type="D")
    _refill_request(PatientFactory.create(), "RX-1")

    rows = {row["id"]: row for row in _find("find_pharmacy_requests", patient)}

    assert {request_id: row["status"] for request_id, row in rows.items()} == {
        str(waiting.id): "waiting",
        str(first_ask.id): "answered",
        str(resent.id): "answered",
        str(ignored.id): "ignored",
    }
    assert (rows[str(resent.id)]["response"], rows[str(resent.id)]["note_dbid"]) == (
        "Denied",
        answer.note_id,
    )
    assert rows[str(waiting.id)] | {"id": None, "received": None} == {
        "id": None,
        "type": "Refill request",
        "received": None,
        "medication": "lisinopril 10 mg tablet",
        "sig": "TAKE 1 TABLET BY MOUTH DAILY",
        "quantity": "30",
        "days_supply": "30",
        "last_fill_date": "2026-09-01",
        "pharmacy": "Corner Pharmacy",
        "status": "waiting",
        "response": None,
        "note_dbid": None,
    }


@pytest.mark.django_db
def test_a_refill_answer_that_failed_to_send_leaves_the_request_waiting() -> None:
    """The pharmacy never got an answer whose sending failed, so it is still waiting."""
    patient = PatientFactory.create()
    request = _refill_request(patient, "RX-1")
    _answer(patient, request, status="error")

    (row,) = _find("find_pharmacy_requests", patient)

    assert (row["id"], row["status"]) == (str(request.id), "waiting")


@pytest.mark.django_db
def test_a_change_request_names_the_change_and_the_medications_proposed() -> None:
    """A substitution request, answered by a committed response."""
    patient = PatientFactory.create()
    request = PrescriptionChangeRequestFactory.create(
        patient=patient,
        type_code="G",
        content={
            "pharmacy": {"name": "Corner Pharmacy"},
            "prescribed_medication": {"drug_description": "Lipitor 40 mg tablet"},
            "requested_medications": [{"drug_description": "atorvastatin 40 mg tablet"}],
        },
    )
    unanswered = PrescriptionChangeRequestFactory.create(patient=patient, type_code="P")
    PrescriptionChangeResponseFactory.create(
        patient=patient,
        request=request,
        response_type="A",
        committer=CanvasUserFactory.create(),
    )

    rows = {row["id"]: row for row in _find("find_pharmacy_requests", patient, kind="change")}

    answered = rows[str(request.id)]
    assert (answered["type"], answered["change"], answered["medication"]) == (
        "Change request",
        "Generic Substitution",
        "Lipitor 40 mg tablet",
    )
    assert answered["requested"] == ["atorvastatin 40 mg tablet"]
    assert (answered["status"], answered["response"]) == ("answered", "Approved")
    assert rows[str(unanswered.id)]["change"] == "Prior Authorization Required"
    assert rows[str(unanswered.id)]["status"] == "waiting"


@pytest.mark.django_db
def test_the_status_filter_finds_waiting_requests_past_the_limit() -> None:
    """A filter on status looks past the newest requests to find the ones asked for."""
    patient = PatientFactory.create()
    old = _refill_request(patient, "RX-OLD")
    for number in range(3):
        _answer(patient, _refill_request(patient, f"RX-{number}"))

    rows = _find("find_pharmacy_requests", patient, status="waiting", limit=1)

    assert [row["id"] for row in rows] == [str(old.id)]


@pytest.mark.django_db
def test_a_pharmacy_request_is_cited_as_one() -> None:
    """The citation card names the medication and where the request stands."""
    patient = PatientFactory.create()
    request = _refill_request(patient, "RX-1")
    rows = _find("find_pharmacy_requests", patient)
    sources = Sources(standard_tools).add_all(
        [
            {
                "role": "assistant",
                "content": [{"type": "tool_use", "id": "t1", "name": "find_pharmacy_requests"}],
            },
            {
                "role": "user",
                "content": [
                    {"type": "tool_result", "tool_use_id": "t1", "content": json.dumps(rows)}
                ],
            },
        ]
    )

    _, (citation,) = cite(f"Waiting on you [[cite:{request.id}]].", sources)

    assert (citation.kind, citation.label, citation.detail) == (
        "Refill request",
        "lisinopril 10 mg tablet",
        "waiting",
    )
