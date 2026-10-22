from decimal import Decimal

import pytest
from appointment_copay_collection.services.copay import (
    CopayStatus,
    charge_idempotency_key,
    copay_rows,
    eligibility_copay,
    parse_copay_amounts,
    stored_cards,
)

from canvas_sdk.test_utils.factories import PatientFactory, PaymentCardFactory
from canvas_sdk.v1.data import Claim, Patient
from canvas_sdk.v1.data.appointment import AppointmentProgressStatus
from canvas_sdk.v1.data.coverage import CoverageState

from .conftest import AppointmentMaker, post_copay, set_coverage_copay, trash


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (
            '{"office-visit": "25", "telehealth": 15.5}',
            {"office-visit": Decimal("25.00"), "telehealth": Decimal("15.50")},
        ),
        ('{"office-visit": "abc", "free": "0", "negative": "-5", "nan": "NaN"}', {}),
        ('["office-visit"]', {}),
        ("not json", {}),
        ("", {}),
        (None, {}),
    ],
)
def test_parse_copay_amounts(raw: str | None, expected: dict[str, Decimal]) -> None:
    """Only positive amounts from a JSON object are kept, rounded to cents."""
    assert parse_copay_amounts(raw) == expected


def test_charge_idempotency_key_is_stable_per_appointment_card_and_amount() -> None:
    """The same payment always gets the same key, and a different card or amount does not."""
    key = charge_idempotency_key("appt", "card", Decimal("25.00"))

    assert key == charge_idempotency_key("appt", "card", Decimal("25.00"))
    assert key != charge_idempotency_key("appt", "other-card", Decimal("25.00"))
    assert key != charge_idempotency_key("appt", "card", Decimal("30.00"))
    assert key != charge_idempotency_key("other-appt", "card", Decimal("25.00"))


@pytest.mark.django_db
def test_eligibility_copay_reads_primary_active_coverage(patient: Patient) -> None:
    """The coverage copay comes from the primary active coverage only, in dollars."""
    set_coverage_copay(patient, 4000, coverage_rank=2)
    assert eligibility_copay(patient.id) is None

    set_coverage_copay(patient, 2500)
    assert eligibility_copay(patient.id) == Decimal("25.00")

    patient.coverages.filter(coverage_rank=1).update(state=CoverageState.DELETED)
    assert eligibility_copay(patient.id) is None


@pytest.mark.django_db
def test_copay_rows_due_with_configured_amount(
    patient: Patient, make_appointment: AppointmentMaker
) -> None:
    """A billable appointment with a claim is due, at the amount configured for its note type."""
    set_coverage_copay(patient, 1000)
    appointment = make_appointment(patient, code="office-visit")

    [row] = copay_rows(patient.id, {"office-visit": Decimal("25.00")})

    assert row["appointment"] == appointment
    assert row["status"] == CopayStatus.DUE
    assert row["amount"] == Decimal("25.00")
    assert row["claim"] == Claim.objects.get(note=appointment.note)


@pytest.mark.django_db
def test_copay_rows_falls_back_to_coverage_copay(
    patient: Patient, make_appointment: AppointmentMaker
) -> None:
    """Without a configured amount for the note type, the primary coverage copay is used."""
    set_coverage_copay(patient, 1500)
    make_appointment(patient, code="office-visit")

    [row] = copay_rows(patient.id, {"telehealth": Decimal("25.00")})

    assert (row["status"], row["amount"]) == (CopayStatus.DUE, Decimal("15.00"))


@pytest.mark.django_db
def test_copay_rows_statuses(patient: Patient, make_appointment: AppointmentMaker) -> None:
    """Paid, non-billable, claimless and amountless appointments are not due."""
    paid = make_appointment(patient, code="paid", days_ahead=1)
    post_copay(Claim.objects.get(note=paid.note), patient, Decimal("25.00"))
    make_appointment(patient, code="not-billable", billable=False, with_claim=False, days_ahead=2)
    make_appointment(patient, code="no-claim", with_claim=False, days_ahead=3)
    make_appointment(patient, code="no-amount", days_ahead=4)

    rows = copay_rows(
        patient.id,
        {"paid": Decimal("25"), "not-billable": Decimal("25"), "no-claim": Decimal("25")},
    )

    assert [(row["appointment"].note_type.code, row["status"], row["amount"]) for row in rows] == [
        ("paid", CopayStatus.PAID, None),
        ("not-billable", CopayStatus.NOT_BILLABLE, None),
        ("no-claim", CopayStatus.NO_CLAIM, None),
        ("no-amount", CopayStatus.NO_AMOUNT, None),
    ]


@pytest.mark.django_db
def test_copay_rows_ignores_trashed_claims(
    patient: Patient, make_appointment: AppointmentMaker
) -> None:
    """A claim in the trash is not charged."""
    appointment = make_appointment(patient)
    trash(Claim.objects.get(note=appointment.note))

    [row] = copay_rows(patient.id, {"office-visit": Decimal("25.00")})

    assert row["status"] == CopayStatus.NO_CLAIM


@pytest.mark.django_db
def test_copay_rows_lists_only_the_patients_upcoming_appointments(
    patient: Patient, make_appointment: AppointmentMaker
) -> None:
    """Past, canceled and no-showed appointments, and other patients' appointments, are left out."""
    upcoming = make_appointment(patient)
    make_appointment(patient, days_ahead=-1)
    make_appointment(patient, status=AppointmentProgressStatus.CANCELLED)
    make_appointment(patient, status=AppointmentProgressStatus.NOSHOWED)
    make_appointment(PatientFactory.create())

    rows = copay_rows(patient.id, {})

    assert [row["appointment"] for row in rows] == [upcoming]


@pytest.mark.django_db
def test_stored_cards_lists_default_card_first(patient: Patient) -> None:
    """The patient's cards are returned default first, and no other patient's cards."""
    other = PaymentCardFactory.create(patient=patient, card_last_four_digits="1111")
    default = PaymentCardFactory.create(
        patient=patient, card_last_four_digits="2222", is_default=True
    )
    PaymentCardFactory.create()

    cards = stored_cards(patient.id)

    assert [card["id"] for card in cards] == [str(default.id), str(other.id)]
    assert cards[0]["last_four"] == "2222"
