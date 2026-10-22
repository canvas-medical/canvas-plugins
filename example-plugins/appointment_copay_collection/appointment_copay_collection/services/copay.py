"""Work out what each upcoming appointment's copay is, and which claim it is charged to.

A billable appointment has a claim from the moment it is booked (appointment → note → claim),
so a copay can be posted to that claim's COPAY line item right away. A non-billable appointment
has no claim, and is never charged.
"""

import json
from decimal import Decimal
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid5

from django.utils import timezone

from canvas_sdk.v1.data import (
    Appointment,
    Claim,
    EligibilitySummary,
    PatientPosting,
    PaymentCard,
)
from canvas_sdk.v1.data.appointment import AppointmentProgressStatus
from canvas_sdk.v1.data.coverage import CoverageStack, CoverageState

COPAY_AMOUNTS_VARIABLE = "COPAY_AMOUNTS"

PRIMARY_COVERAGE_RANK = 1

CENTS = Decimal("0.01")

UNPAYABLE_STATUSES = (AppointmentProgressStatus.CANCELLED, AppointmentProgressStatus.NOSHOWED)


class CopayStatus:
    """Where an appointment stands with its copay."""

    DUE = "due"
    PAID = "paid"
    NOT_BILLABLE = "not_billable"
    NO_CLAIM = "no_claim"
    NO_AMOUNT = "no_amount"


def parse_copay_amounts(raw: str | None) -> dict[str, Decimal]:
    """Parse the COPAY_AMOUNTS variable into note type code → copay in dollars.

    The variable is a JSON object such as ``{"office-visit": "25.00"}``. Entries whose amount
    is not a positive number are skipped, and anything that is not a JSON object yields no
    amounts.
    """
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}

    amounts: dict[str, Decimal] = {}
    for code, value in data.items():
        try:
            amount = Decimal(str(value))
        except ArithmeticError:
            continue
        if amount.is_finite() and amount > 0:
            amounts[str(code)] = amount.quantize(CENTS)
    return amounts


def eligibility_copay(patient_id: str) -> Decimal | None:
    """Return the copay on the patient's primary active coverage, in dollars, if one is recorded."""
    copay_cents = (
        EligibilitySummary.objects.filter(
            coverage__patient__id=patient_id,
            coverage__coverage_rank=PRIMARY_COVERAGE_RANK,
            coverage__state=CoverageState.ACTIVE,
            coverage__stack=CoverageStack.IN_USE,
            copay_cents__gt=0,
        )
        .order_by("-coverage__created")
        .values_list("copay_cents", flat=True)
        .first()
    )
    if copay_cents is None:
        return None
    return (Decimal(copay_cents) / 100).quantize(CENTS)


def charge_idempotency_key(appointment_id: str, payment_card_id: str, amount: Decimal) -> UUID:
    """Return the idempotency key for charging an appointment's copay.

    The same appointment, card and amount always map to the same key, so a repeated submission
    reaches the payment processor as a retry of one charge rather than as a second charge.
    """
    return uuid5(NAMESPACE_URL, f"appointment-copay:{appointment_id}:{payment_card_id}:{amount}")


def upcoming_appointments(patient_id: str) -> list[Appointment]:
    """Return the patient's upcoming appointments that can still take place, soonest first."""
    return list(
        Appointment.objects.filter(
            patient__id=patient_id,
            start_time__gte=timezone.now(),
            entered_in_error__isnull=True,
        )
        .exclude(status__in=UNPAYABLE_STATUSES)
        .select_related("note_type", "provider", "location")
        .order_by("start_time")
    )


def claims_by_note(note_dbids: list[int]) -> dict[int, Claim]:
    """Return the newest active claim of each note, keyed by the note's dbid."""
    claims: dict[int, Claim] = {}
    for claim in Claim.objects.active().filter(note_id__in=note_dbids).order_by("created"):
        claims[claim.note_id] = claim
    return claims


def claims_with_copay(claim_dbids: list[int]) -> set[int]:
    """Return the dbids of the claims that already have a copay payment posted."""
    return set(
        PatientPosting.objects.active()
        .filter(claim_id__in=claim_dbids, copay__isnull=False)
        .values_list("claim_id", flat=True)
    )


def copay_rows(patient_id: str, configured_amounts: dict[str, Decimal]) -> list[dict[str, Any]]:
    """Describe each upcoming appointment with its copay amount, claim and status."""
    appointments = upcoming_appointments(patient_id)
    claims = claims_by_note([a.note_id for a in appointments if a.note_id is not None])
    paid_claims = claims_with_copay([claim.dbid for claim in claims.values()])
    coverage_copay = eligibility_copay(patient_id)

    rows = []
    for appointment in appointments:
        note_type = appointment.note_type
        claim = claims.get(appointment.note_id) if appointment.note_id is not None else None
        amount = (configured_amounts.get(note_type.code) if note_type else None) or coverage_copay

        if note_type is None or not note_type.is_billable:
            status = CopayStatus.NOT_BILLABLE
        elif claim is None:
            status = CopayStatus.NO_CLAIM
        elif claim.dbid in paid_claims:
            status = CopayStatus.PAID
        elif amount is None:
            status = CopayStatus.NO_AMOUNT
        else:
            status = CopayStatus.DUE

        rows.append(
            {
                "appointment": appointment,
                "claim": claim,
                "amount": amount if status == CopayStatus.DUE else None,
                "status": status,
            }
        )
    return rows


def stored_cards(patient_id: str) -> list[dict[str, Any]]:
    """Return the patient's stored cards, default card first."""
    return [
        {
            "id": str(card["id"]),
            "brand": card["brand"],
            "last_four": card["card_last_four_digits"],
            "expiration_month": card["expiration_month"],
            "expiration_year": card["expiration_year"],
        }
        for card in PaymentCard.objects.filter(patient__id=patient_id)
        .order_by("-is_default", "created")
        .values(
            "id",
            "brand",
            "card_last_four_digits",
            "expiration_month",
            "expiration_year",
        )
    ]
