from collections.abc import Callable
from decimal import Decimal

import pytest

from canvas_generated.messages.events_pb2 import Event as EventRequest
from canvas_generated.messages.events_pb2 import EventType
from canvas_sdk.effects import Effect
from canvas_sdk.events import Event
from canvas_sdk.protocols import ClinicalQualityMeasure
from canvas_sdk.test_utils.factories import (
    ImagingReportFactory,
    LabReportFactory,
    NoteFactory,
    PatientFactory,
    ReferralReportFactory,
)
from canvas_sdk.v1.data import Patient
from canvas_sdk.v1.data.base import IdentifiableModel
from canvas_sdk.v1.data.billing import BillingLineItem
from canvas_sdk.v1.data.instruction import Instruction
from canvas_sdk.v1.data.questionnaire import Interview


class Measure(ClinicalQualityMeasure):
    """Concrete measure for exercising the base class."""

    def compute(self) -> list[Effect]:
        """No effects."""
        return []


def _measure(event_type: EventType, target: str) -> Measure:
    return Measure(Event(EventRequest(type=event_type, target=target)))


def _interview(patient: Patient | None) -> Interview:
    return Interview.objects.create(
        patient=patient,
        deleted=False,
        status="AC",
        name="Tobacco use",
        language_id=1,
        use_case_in_charting="QUES",
        note_id=1,
        appointment_id=1,
        progress_status="F",
    )


def _instruction(patient: Patient) -> Instruction:
    return Instruction.objects.create(
        patient=patient, note=NoteFactory.create(patient=patient), narrative="Quit smoking"
    )


def _lab_report(patient: Patient) -> IdentifiableModel:
    return LabReportFactory.create(patient=patient)


def _referral_report(patient: Patient) -> IdentifiableModel:
    return ReferralReportFactory.create(patient=patient)


def _billing_line_item(patient: Patient) -> BillingLineItem:
    return BillingLineItem.objects.create(
        patient=patient, charge=Decimal("100.00"), units=1, command_id=1
    )


def _imaging_report(patient: Patient) -> IdentifiableModel:
    return ImagingReportFactory.create(patient=patient)


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("event_types", "make_target"),
    [
        ((EventType.LAB_REPORT_CREATED, EventType.LAB_REPORT_UPDATED), _lab_report),
        ((EventType.INTERVIEW_CREATED, EventType.INTERVIEW_UPDATED), _interview),
        ((EventType.INSTRUCTION_CREATED, EventType.INSTRUCTION_UPDATED), _instruction),
        (
            (EventType.REFERRAL_REPORT_CREATED, EventType.REFERRAL_REPORT_UPDATED),
            _referral_report,
        ),
        (
            (EventType.BILLING_LINE_ITEM_CREATED, EventType.BILLING_LINE_ITEM_UPDATED),
            _billing_line_item,
        ),
        (
            (EventType.IMAGING_REPORT_CREATED, EventType.IMAGING_REPORT_UPDATED),
            _imaging_report,
        ),
    ],
)
def test_patient_id_from_target_resolves_the_targets_patient(
    event_types: tuple[EventType, EventType],
    make_target: Callable[[Patient], IdentifiableModel],
) -> None:
    """Events targeting a patient-owned record resolve to that record's patient."""
    patient = PatientFactory.create()
    target = make_target(patient)
    for event_type in event_types:
        assert _measure(event_type, str(target.id)).patient_id_from_target() == str(patient.id)


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("event_type", "make_target"),
    [
        (EventType.LAB_REPORT_UPDATED, _lab_report),
        (EventType.INTERVIEW_UPDATED, _interview),
        (EventType.INSTRUCTION_UPDATED, _instruction),
    ],
)
def test_patient_id_from_target_resolves_a_soft_deleted_target(
    event_type: EventType,
    make_target: Callable[[Patient], IdentifiableModel],
) -> None:
    """Removing a command soft-deletes its record and sends *_UPDATED, which must still resolve."""
    patient = PatientFactory.create()
    target = make_target(patient)
    type(target)._base_manager.filter(pk=target.pk).update(deleted=True)
    assert _measure(event_type, str(target.id)).patient_id_from_target() == str(patient.id)


@pytest.mark.django_db
def test_patient_id_from_target_rejects_a_missing_target() -> None:
    """A target id with no record raises ValueError."""
    measure = _measure(EventType.INTERVIEW_UPDATED, "00000000000000000000000000000000")
    with pytest.raises(ValueError, match="No patient found"):
        measure.patient_id_from_target()


@pytest.mark.django_db
def test_patient_id_from_target_uses_patient_events_target_directly() -> None:
    """Patient events target the patient itself."""
    patient = PatientFactory.create()
    measure = _measure(EventType.PATIENT_UPDATED, str(patient.id))
    assert measure.patient_id_from_target() == str(patient.id)


@pytest.mark.django_db
def test_patient_id_from_target_rejects_a_target_without_a_patient() -> None:
    """An interview with no patient raises instead of returning None."""
    interview = _interview(None)
    measure = _measure(EventType.INTERVIEW_CREATED, str(interview.id))
    with pytest.raises(ValueError, match="No patient found"):
        measure.patient_id_from_target()


def test_patient_id_from_target_rejects_unsupported_event_types() -> None:
    """Event types without a patient-bearing target raise ValueError."""
    measure = _measure(EventType.APPOINTMENT_CREATED, "some-id")
    with pytest.raises(ValueError, match="not supported"):
        measure.patient_id_from_target()
