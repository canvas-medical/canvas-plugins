from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.effects import EffectType, _BaseEffect
from canvas_sdk.v1.data import Claim, Patient


class ChargeStoredCard(_BaseEffect):
    """Charge a patient's stored payment card through Canvas's configured payment processor.

    The charge is processed server-side using the patient's stored card on file, so no
    card data ever crosses the plugin boundary. For the built-in Stripe processor,
    reference the card by its Canvas id (see the ``PaymentCard`` data model); a custom
    payment processor manages its own cards, so ``payment_card_id`` is whatever reference
    that processor understands.

    ``amount`` is a decimal dollar amount (e.g. ``Decimal("49.99")``), matching how Canvas
    records collected payments.

    An ``idempotency_key`` is required on every charge. Reusing the same key for a retry
    guarantees the patient is not charged twice. The key must be **stable across retries
    of the same logical charge** -- generate it deterministically (e.g.
    ``uuid.uuid5(namespace, f"appointment-{id}-charge")``) or persist a ``uuid4`` before
    emitting, rather than generating a fresh key on every attempt.

    The payment is always applied to the patient's account:

    * No ``claim_id`` -> allocated across the patient's outstanding balance (rejected if the
      amount exceeds the total balance).
    * ``claim_id`` with ``copay=False`` (default) -> pays down that claim's line-item
      balances; rejected if the claim has nothing to charge against.
    * ``claim_id`` with ``copay=True`` -> recorded as a copay on that claim (posted to its
      COPAY line item), the way copays are collected in the app. Use this to collect a copay
      or prepayment against a claim that has no outstanding balance. Requires ``claim_id``.

    Compliance note: customers are responsible for obtaining patient consent before
    charging a stored card. Canvas does not enforce consent.
    """

    class Meta:
        effect_type = EffectType.REVENUE__STORED_CARD__CHARGE

    patient_id: str
    payment_card_id: str
    amount: Decimal = Field(gt=0, decimal_places=2)
    idempotency_key: UUID = Field(strict=False)
    claim_id: UUID | str | None = None
    copay: bool = False
    description: str | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if not Patient.objects.filter(id=self.patient_id).exists():
            errors.append(
                self._create_error_detail(
                    "patient_id",
                    f"Patient with id: {self.patient_id} does not exist.",
                    self.patient_id,
                )
            )

        # payment_card_id is intentionally not validated: for the built-in processor it is a
        # stored card, but a custom processor manages its own cards (not saved as a Canvas
        # PaymentCard), so the reference is opaque here and resolved server-side.
        if self.claim_id and not Claim.objects.filter(id=self.claim_id).exists():
            errors.append(
                self._create_error_detail(
                    "claim_id",
                    f"Claim with id: {self.claim_id} does not exist.",
                    self.claim_id,
                )
            )

        if self.copay and not self.claim_id:
            errors.append(
                self._create_error_detail(
                    "copay",
                    "A copay charge requires a claim_id to post the copay against.",
                    self.copay,
                )
            )

        return errors

    @property
    def values(self) -> dict[str, Any]:
        """Return the values of the ChargeStoredCard effect."""
        return {
            "patient_id": self.patient_id,
            "payment_card_id": self.payment_card_id,
            "amount": str(self.amount),
            "idempotency_key": str(self.idempotency_key),
            "claim_id": str(self.claim_id) if self.claim_id else None,
            "copay": self.copay,
            "description": self.description,
        }


__exports__ = ("ChargeStoredCard",)
