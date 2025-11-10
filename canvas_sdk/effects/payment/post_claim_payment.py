from typing import Any

from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType
from canvas_sdk.effects.payment.base import ClaimAllocation, PostPaymentBase
from canvas_sdk.v1.data import Claim


class PostClaimPayment(PostPaymentBase):
    """
    An Effect that posts a coverage or patient payment to a claim.
    """

    class Meta:
        effect_type = EffectType.POST_CLAIM_PAYMENT

    claim: ClaimAllocation

    @property
    def values(self) -> dict[str, Any]:
        """The values for the payload."""
        return {
            "posting": {
                "claim_id": str(self.claim.claim_id),
                "claim_coverage_id": str(self.claim.claim_coverage_id),
                "description": self.posting_description,
            },
            "payment_collection": self.payment_collection_values,
            "line_item_transactions": [t.to_dict() for t in self.claim.line_item_transactions],
            "move_to_queue_name": self.claim.move_to_queue_name,
        }

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if not (claim := Claim.objects.get(id=self.claim.claim_id)):
            errors.append(
                self._create_error_detail(
                    "value",
                    "The provided claim_id does not correspond with an existing Claim",
                    self.claim.claim_id,
                )
            )
        errors.extend([self._create_error_detail(*e) for e in self.claim.validate(claim)])
        errors.extend(self.validate_payment_method_fields())

        return errors


__exports__ = (
    "PaymentMethod",
    "PostClaimPayment",
    "ClaimAllocation",
)
