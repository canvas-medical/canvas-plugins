from decimal import Decimal
from typing import Any

from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType
from canvas_sdk.effects.payment.base import ClaimAllocation, PostPaymentBase


class PostClaimPayment(PostPaymentBase):
    """
    An Effect that posts a coverage or patient payment to a claim.
    """

    class Meta:
        effect_type = EffectType.POST_CLAIM_PAYMENT

    claim: ClaimAllocation

    @property
    def total_collected(self) -> str:
        """The total amount collected for this payment, calculated as sum of payments from line item transactions."""
        total = sum((item.payment or Decimal(0)) for item in self.claim.line_item_transactions)
        return str(total)

    @property
    def payment_collection_values(self) -> dict[str, Any]:
        """The values for the payment collection part of the payload."""
        base_values = super().payment_collection_values
        return base_values | {"total_collected": self.total_collected}

    @property
    def values(self) -> dict[str, Any]:
        """The values for the payload."""
        return {
            "payment_collection": self.payment_collection_values,
            "claims_allocation": [self.claim.to_dict()],
        }

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        errors.extend([self._create_error_detail(*e) for e in self.claim.validate()])
        errors.extend(self.validate_payment_method_fields())

        return errors


__exports__ = ("PostClaimPayment",)
