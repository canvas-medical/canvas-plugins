from datetime import timedelta
from decimal import Decimal
from typing import Protocol

import pytest
from django.utils import timezone

from canvas_sdk.test_utils.factories import (
    ClaimFactory,
    ClaimQueueFactory,
    CoverageFactory,
    NoteFactory,
    NoteTypeFactory,
    PatientFactory,
    PaymentCollectionFactory,
)
from canvas_sdk.v1.data import (
    Appointment,
    BulkPatientPosting,
    Claim,
    ClaimPatient,
    EligibilitySummary,
    Patient,
    PatientPosting,
)
from canvas_sdk.v1.data.appointment import AppointmentProgressStatus

TRASH_QUEUE = 10


class AppointmentMaker(Protocol):
    """Builds an appointment for a patient."""

    def __call__(
        self,
        patient: Patient,
        *,
        code: str = ...,
        billable: bool = ...,
        with_claim: bool = ...,
        days_ahead: int = ...,
        status: str = ...,
    ) -> Appointment:
        """Create the appointment."""
        ...


@pytest.fixture
def patient() -> Patient:
    """A patient with nothing on file."""
    return PatientFactory.create()


@pytest.fixture
def make_appointment() -> AppointmentMaker:
    """Return a builder for appointments, with a note and (optionally) a claim like booking makes."""

    def build(
        patient: Patient,
        *,
        code: str = "office-visit",
        billable: bool = True,
        with_claim: bool = True,
        days_ahead: int = 3,
        status: str = AppointmentProgressStatus.CONFIRMED,
    ) -> Appointment:
        note_type = NoteTypeFactory.create(code=code, is_billable=billable)
        note = NoteFactory.create(patient=patient, note_type_version=note_type)
        if with_claim:
            ClaimFactory.create(note=note)
        return Appointment.objects.create(
            patient=patient,
            note=note,
            note_type=note_type,
            provider=note.provider,
            location=note.location,
            start_time=timezone.now() + timedelta(days=days_ahead),
            duration_minutes=30,
            status=status,
            telehealth_instructions_sent=False,
        )

    return build


def set_coverage_copay(patient: Patient, copay_cents: int, *, coverage_rank: int = 1) -> None:
    """Record a copay on a new active coverage of the given rank."""
    coverage = CoverageFactory.create(patient=patient, coverage_rank=coverage_rank)
    EligibilitySummary.objects.create(coverage=coverage, copay_cents=copay_cents)


def post_copay(claim: Claim, patient: Patient, amount: Decimal) -> None:
    """Post a copay payment to a claim, as the staff copay flow and the interpreter do."""
    bulk = BulkPatientPosting.objects.create(
        payment_collection=PaymentCollectionFactory.create(total_collected=amount),
        total_paid=amount,
        payer=patient,
    )
    claim_patient = ClaimPatient.objects.create(claim=claim)
    PatientPosting.objects.create(
        claim=claim, claim_patient=claim_patient, patient_payment=bulk, copay=bulk
    )


def trash(claim: Claim) -> None:
    """Move a claim to the trash queue."""
    claim.current_queue = ClaimQueueFactory.create(queue_sort_ordering=TRASH_QUEUE, name="Trash")
    claim.save()
