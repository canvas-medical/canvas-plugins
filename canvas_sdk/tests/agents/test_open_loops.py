"""find_open_loops: each order with whether its result came back and was reviewed."""

import json
from datetime import date, timedelta
from typing import Any

import pytest
from django.utils import timezone

from canvas_sdk.agents import standard_tools
from canvas_sdk.agents.citations import Sources, cite
from canvas_sdk.test_utils.factories import (
    CanvasUserFactory,
    ImagingOrderFactory,
    ImagingReportFactory,
    ImagingReviewFactory,
    LabOrderFactory,
    LabReportFactory,
    LabReviewFactory,
    LabTestFactory,
    PatientFactory,
    ReferralFactory,
    ReferralReportFactory,
    ReferralReviewFactory,
    ServiceProviderFactory,
)
from canvas_sdk.v1.data import LabTest
from canvas_sdk.v1.data.common import OrderStatus, ReviewStatus

Status = LabTest.LabTestOrderStatus


def _days_ago(days: int) -> Any:
    return timezone.now() - timedelta(days=days)


def _lab_order(patient: Any, *tests: tuple[str, str, Any], days: int = 10, **fields: Any) -> Any:
    """A committed lab order placed ``days`` ago with tests of (name, status, report)."""
    order = LabOrderFactory.create(
        patient=patient,
        date_ordered=_days_ago(days),
        committer=CanvasUserFactory.create(),
        **fields,
    )
    for name, status, report in tests:
        LabTestFactory.create(order=order, ontology_test_name=name, status=status, report=report)
    return order


def _loops(patient: Any, **arguments: Any) -> list[dict[str, Any]]:
    return standard_tools.execute("find_open_loops", arguments, ctx={"patient_id": patient.id})


@pytest.mark.django_db
def test_a_lab_order_with_no_result_is_open_and_says_how_long() -> None:
    """The clinician learns the labs never came back, and since when."""
    patient = PatientFactory.create()
    order = _lab_order(patient, ("CBC", Status.PROCESSING, None))

    (loop,) = _loops(patient)

    assert loop["id"] == str(order.id)
    assert (loop["type"], loop["item"], loop["status"]) == ("Lab order", "CBC", "awaiting_result")
    assert loop["days_waiting"] == 10
    assert loop["summary"] == "No result after 10 days"
    assert loop["note_dbid"] == order.note.dbid


@pytest.mark.django_db
def test_a_result_nobody_reviewed_is_open() -> None:
    """A result sitting unreviewed is the most actionable loop."""
    patient = PatientFactory.create()
    report = LabReportFactory.create(patient=patient, original_date=_days_ago(3))
    _lab_order(patient, ("CMP", Status.RECEIVED, report))

    (loop,) = _loops(patient)

    assert loop["status"] == "awaiting_review"
    assert loop["days_waiting"] == 3
    assert loop["summary"] == f"Result received {loop['resulted_on']}, not reviewed"


@pytest.mark.django_db
def test_a_reviewed_order_is_closed_and_shown_only_when_asked() -> None:
    """Closed loops stay out of the way unless the clinician wants the whole picture."""
    patient = PatientFactory.create()
    review = LabReviewFactory.create(patient=patient, status=ReviewStatus.STATUS_REVIEWED)
    report = LabReportFactory.create(patient=patient, review=review)
    _lab_order(patient, ("Lipid panel", Status.RECEIVED, report))
    _lab_order(patient, ("A1c", Status.REVIEWED, None))

    assert _loops(patient) == []
    closed = _loops(patient, include_closed=True)
    assert {(loop["item"], loop["status"]) for loop in closed} == {
        ("Lipid panel", "closed"),
        ("A1c", "closed"),
    }


@pytest.mark.django_db
def test_an_order_with_a_test_still_out_names_it() -> None:
    """Some tests back and reviewed, one still out: open, and the summary says which."""
    patient = PatientFactory.create()
    _lab_order(patient, ("CBC", Status.REVIEWED, None), ("Vitamin D", Status.PROCESSING, None))

    (loop,) = _loops(patient)

    assert loop["status"] == "awaiting_result"
    assert loop["pending_tests"] == ["Vitamin D"]
    assert loop["summary"] == "No result for Vitamin D after 10 days"


@pytest.mark.django_db
def test_an_unreviewed_result_outranks_a_test_still_out() -> None:
    """When one test is back unreviewed and another is out, the review is what waits."""
    patient = PatientFactory.create()
    report = LabReportFactory.create(patient=patient)
    _lab_order(patient, ("CBC", Status.RECEIVED, report), ("Vitamin D", Status.PROCESSING, None))

    (loop,) = _loops(patient)

    assert loop["status"] == "awaiting_review"
    assert loop["pending_tests"] == ["Vitamin D"]
    assert loop["summary"].endswith(", not reviewed; no result yet for Vitamin D")


@pytest.mark.django_db
def test_only_committed_orders_on_the_patient_with_active_tests_count() -> None:
    """Only committed orders on this patient count, and an inactive test is not waited on."""
    patient = PatientFactory.create()
    _lab_order(patient, ("Old panel", Status.INACTIVE, None))
    _lab_order(PatientFactory.create(), ("CBC", Status.PROCESSING, None))
    draft = LabOrderFactory.create(patient=patient, committer=None)
    LabTestFactory.create(order=draft, status=Status.NEW, report=None)
    _lab_order(patient, ("CBC", Status.PROCESSING, None), ("Old panel", Status.INACTIVE, None))

    (loop,) = _loops(patient)

    assert loop["item"] == "CBC"


@pytest.mark.django_db
def test_imaging_is_open_until_a_report_comes_back_and_is_reviewed() -> None:
    """A study never done, a report unreviewed, and a cancelled order that will never report."""
    patient = PatientFactory.create()
    committer = CanvasUserFactory.create()
    ImagingOrderFactory.create(
        patient=patient, imaging="MRI brain", date_time_ordered=_days_ago(20), committer=committer
    )
    reported = ImagingOrderFactory.create(
        patient=patient, imaging="Chest X-ray", date_time_ordered=_days_ago(5), committer=committer
    )
    ImagingReportFactory.create(patient=patient, order=reported, result_date=date.today())
    reviewed = ImagingOrderFactory.create(patient=patient, imaging="Echo", committer=committer)
    ImagingReportFactory.create(
        patient=patient,
        order=reviewed,
        review=ImagingReviewFactory.create(patient=patient, status=ReviewStatus.STATUS_REVIEWED),
    )
    ImagingOrderFactory.create(
        patient=patient, imaging="CT", status=OrderStatus.CANCELLED, committer=committer
    )

    loops = {loop["item"]: loop for loop in _loops(patient)}

    assert set(loops) == {"MRI brain", "Chest X-ray"}
    assert loops["MRI brain"]["summary"] == "No result after 20 days"
    assert loops["Chest X-ray"]["status"] == "awaiting_review"
    assert loops["Chest X-ray"]["type"] == "Imaging order"


@pytest.mark.django_db
def test_a_referral_waits_for_its_consult_report() -> None:
    """'Why didn't I get the consult report?' is answered with the specialist and the wait."""
    patient = PatientFactory.create()
    committer = CanvasUserFactory.create()
    cardiology = ServiceProviderFactory.create(first_name="Heart", last_name="Partners")
    ReferralFactory.create(
        patient=patient,
        service_provider=cardiology,
        clinical_question="Palpitations",
        date_referred=_days_ago(41),
        committer=committer,
    )
    noted = ReferralFactory.create(patient=patient, committer=committer)
    ReferralReportFactory.create(
        patient=patient,
        referral=noted,
        review=ReferralReviewFactory.create(patient=patient, status="reviewing"),
    )

    loops = {loop["status"]: loop for loop in _loops(patient)}

    waiting = loops["awaiting_result"]
    assert (waiting["type"], waiting["item"]) == ("Referral", "Heart Partners")
    assert waiting["clinical_question"] == "Palpitations"
    assert waiting["summary"] == "No consult report after 41 days"
    assert loops["awaiting_review"]["summary"].startswith("Consult report received")


@pytest.mark.django_db
def test_orders_before_the_window_are_left_out() -> None:
    """'Since the last visit' passes that visit's date; the default looks back 180 days."""
    patient = PatientFactory.create()
    _lab_order(patient, ("Recent", Status.PROCESSING, None), days=10)
    _lab_order(patient, ("Last spring", Status.PROCESSING, None), days=200)

    assert [loop["item"] for loop in _loops(patient)] == ["Recent"]
    since = (timezone.now() - timedelta(days=5)).date().isoformat()
    assert _loops(patient, ordered_on_or_after=since) == []


@pytest.mark.django_db
def test_an_open_loop_is_cited_as_its_order_and_links_to_the_visit() -> None:
    """A reply citing a loop shows the order and can scroll the chart to the note it was placed on."""
    patient = PatientFactory.create()
    order = _lab_order(patient, ("CBC", Status.PROCESSING, None))
    loops = _loops(patient)
    sources = Sources(standard_tools).add_all(
        [
            {
                "role": "assistant",
                "content": [{"type": "tool_use", "id": "t1", "name": "find_open_loops"}],
            },
            {
                "role": "user",
                "content": [
                    {"type": "tool_result", "tool_use_id": "t1", "content": json.dumps(loops)}
                ],
            },
        ]
    )

    text, (citation,) = cite(f"The CBC never resulted [[cite:{order.id}]].", sources)

    assert text == "The CBC never resulted [1]."
    assert (citation.kind, citation.label, citation.detail) == (
        "Lab order",
        "CBC",
        "No result after 10 days",
    )
    assert citation.note_dbid == order.note.dbid


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("days", "summary"),
    [
        (0, "No result yet, ordered today"),
        (1, "No result after 1 day"),
        (2, "No result after 2 days"),
    ],
)
def test_the_wait_reads_naturally(days: int, summary: str) -> None:
    """Same-day and one-day waits read as a person would say them."""
    patient = PatientFactory.create()
    _lab_order(patient, ("CBC", Status.PROCESSING, None), days=days)

    (loop,) = _loops(patient)

    assert loop["summary"] == summary


@pytest.mark.django_db
def test_another_patients_orders_are_absent() -> None:
    """With orders of every kind on two charts, only the run's patient's are reconciled."""
    patient, other = PatientFactory.create(), PatientFactory.create()
    committer = CanvasUserFactory.create()
    for owner in (patient, other):
        _lab_order(owner, ("CBC", Status.PROCESSING, None))
        ImagingOrderFactory.create(patient=owner, imaging="MRI", committer=committer)
        ReferralFactory.create(patient=owner, committer=committer)

    loops = _loops(patient)

    assert sorted(loop["type"] for loop in loops) == ["Imaging order", "Lab order", "Referral"]
    assert {loop["note_dbid"] for loop in loops}.isdisjoint(
        {order.note.dbid for order in other.lab_orders.all()}
    )
