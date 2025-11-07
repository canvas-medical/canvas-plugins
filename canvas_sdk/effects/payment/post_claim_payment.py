from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType
from canvas_sdk.effects.payment.base import LineItemTransaction, PaymentMethod, PostPaymentBase
from canvas_sdk.v1.data import Claim


class PostClaimPayment(PostPaymentBase):
    """
    An Effect that posts a coverage or patient payment to a claim.
    """

    class Meta:
        effect_type = EffectType.POST_CLAIM_PAYMENT

    claim_id: str | UUID
    subscriber_number: str | None = None
    move_to_queue_name: str | None = None
    line_item_transactions: list[LineItemTransaction]

    @property
    def values(self) -> dict[str, Any]:
        """The values for the payload."""
        return {
            "posting": {
                "claim_id": str(self.claim_id),
                "payer_id": str(self.payer_id),
                "subscriber_number": self.subscriber_number,
                "description": self.posting_description,
            },
            "payment_collection": self.payment_collection_values,
            "line_item_transactions": [t.to_dict() for t in self.line_item_transactions],
            "move_to_queue_name": self.move_to_queue_name,
        }

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        claim = Claim.objects.get(id=self.claim_id)
        if not claim:
            errors.append(
                self._create_error_detail(
                    "value",
                    "Claim does not exist",
                    self.claim_id,
                )
            )

        if not claim.coverages.active().filter(payer_id=self.payer_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    "Payer is not active for this claim",
                    self.payer_id,
                )
            )

        if self.method == PaymentMethod.CHECK and not self.check_date and not self.check_number:
            errors.append(
                self._create_error_detail(
                    "value",
                    "Check date and check number are required when payment method is 'check'",
                    self.method.value,
                )
            )

        return errors


__exports__ = (
    "PaymentMethod",
    "PostClaimPayment",
    "LineItemTransaction",
)
