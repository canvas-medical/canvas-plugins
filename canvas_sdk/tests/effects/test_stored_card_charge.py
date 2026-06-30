import json
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.payment.stored_card_charge import ChargeStoredCard
from canvas_sdk.test_utils.factories import ClaimFactory, PatientFactory
from canvas_sdk.v1.data import Patient


def _charge(
    patient_id: str,
    payment_card_id: str,
    *,
    amount: Any = Decimal("10.00"),
    idempotency_key: Any = None,
    claim_id: Any = None,
    copay: bool = False,
    description: str | None = None,
) -> ChargeStoredCard:
    """Build a ChargeStoredCard with sensible defaults, overridable per-test."""
    return ChargeStoredCard(
        patient_id=patient_id,
        payment_card_id=payment_card_id,
        amount=amount,
        idempotency_key=uuid4() if idempotency_key is None else idempotency_key,
        claim_id=claim_id,
        copay=copay,
        description=description,
    )


@pytest.fixture
def patient(db: None) -> Patient:
    """A patient created in the test database."""
    return PatientFactory.create()


@pytest.mark.django_db
def test_effect_type(patient: Patient) -> None:
    """The applied effect carries the stored-card charge effect type."""
    applied = _charge(patient.id, "card-1").apply()
    assert applied.type == EffectType.REVENUE__STORED_CARD__CHARGE


@pytest.mark.django_db
def test_payload_serializes_idempotency_key_as_string(patient: Patient) -> None:
    """The payload includes every field and serializes the UUID key to a string."""
    key = uuid4()
    applied = _charge(
        patient.id,
        "card-1",
        idempotency_key=key,
        amount=Decimal("25.00"),
        description="GLP-1 subscription",
    ).apply()
    payload = json.loads(applied.payload)

    assert payload == {
        "data": {
            "patient_id": patient.id,
            "payment_card_id": "card-1",
            "amount": "25.00",
            "idempotency_key": str(key),
            "claim_id": None,
            "copay": False,
            "description": "GLP-1 subscription",
        }
    }


@pytest.mark.django_db
def test_payment_card_id_not_validated(patient: Patient) -> None:
    """payment_card_id is opaque: an arbitrary, non-UUID reference is accepted as-is.

    A custom processor manages its own cards, so the id need not be a Canvas PaymentCard.
    """
    reference = "processor-owned-token-not-a-uuid"
    payload = json.loads(_charge(patient.id, reference).apply().payload)
    assert payload["data"]["payment_card_id"] == reference


@pytest.mark.django_db
def test_claim_id_serialized_when_claim_exists(patient: Patient) -> None:
    """A provided, existing claim_id is serialized as a string for specific-claim allocation."""
    claim = ClaimFactory.create()
    payload = json.loads(_charge(patient.id, "card-1", claim_id=claim.id).apply().payload)
    assert payload["data"]["claim_id"] == str(claim.id)


@pytest.mark.django_db
def test_claim_id_defaults_to_none(patient: Patient) -> None:
    """Without a claim_id the payload carries null (account-balance allocation)."""
    payload = json.loads(_charge(patient.id, "card-1").apply().payload)
    assert payload["data"]["claim_id"] is None


@pytest.mark.django_db
def test_copay_serialized_when_set(patient: Patient) -> None:
    """A copay charge against a claim serializes copay=True in the payload."""
    claim = ClaimFactory.create()
    payload = json.loads(
        _charge(patient.id, "card-1", claim_id=claim.id, copay=True).apply().payload
    )
    assert payload["data"]["copay"] is True


@pytest.mark.django_db
def test_copay_requires_claim_id(patient: Patient) -> None:
    """A copay charge without a claim_id is rejected (nothing to post the copay against)."""
    with pytest.raises(ValidationError, match="copay charge requires a claim_id"):
        _charge(patient.id, "card-1", copay=True).apply()


@pytest.mark.django_db
def test_unknown_patient_rejected() -> None:
    """Charging a patient that does not exist raises a validation error."""
    with pytest.raises(ValidationError, match="Patient with id"):
        _charge("does-not-exist", "card-1").apply()


@pytest.mark.django_db
def test_unknown_claim_rejected(patient: Patient) -> None:
    """A claim_id that does not exist raises a validation error."""
    with pytest.raises(ValidationError, match="Claim with id"):
        _charge(patient.id, "card-1", claim_id=uuid4()).apply()


def test_idempotency_key_accepts_uuid_string() -> None:
    """A UUID-parseable string is coerced to a UUID at construction time."""
    key = "12345678-1234-5678-1234-567812345678"
    charge = _charge("patient-1", "card-1", idempotency_key=key)
    assert charge.idempotency_key == UUID(key)


def test_idempotency_key_rejects_non_uuid() -> None:
    """A non-UUID idempotency key is rejected at construction."""
    with pytest.raises(ValidationError):
        _charge("patient-1", "card-1", idempotency_key="not-a-uuid")


def test_idempotency_key_is_required() -> None:
    """Omitting the idempotency key is a validation error."""
    with pytest.raises(ValidationError):
        ChargeStoredCard(  # type: ignore[call-arg]
            patient_id="patient-1", payment_card_id="card-1", amount=Decimal("10.00")
        )


@pytest.mark.parametrize("amount", [Decimal("0"), Decimal("-1.00")])
def test_amount_must_be_positive(amount: Decimal) -> None:
    """A non-positive amount is rejected at construction."""
    with pytest.raises(ValidationError):
        _charge("patient-1", "card-1", amount=amount)
