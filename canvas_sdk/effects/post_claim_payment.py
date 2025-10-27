from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect
from canvas_sdk.v1.data import Claim

# this_works = {
#     "paymentCollection": {
#         "lineItemTransactions": [
#             {
#                 "adjustment": 30,
#                 "adjustmentType": "CO-45",
#                 "allowed": 20,
#                 "automatedBehavior": "write_off",
#                 "claimLineItemId": "Q2xhaW1MaW5lSXRlbVR5cGU6Mw==",
#                 "payment": 20,
#                 "transferTo": "Q2xhaW1QYXRpZW50VHlwZTox",
#                 "writeOff": "false",
#             }
#         ],
#         "paymentCollection": {
#             "checkDate": "2025-10-27",
#             "checkNumber": "123445",
#             "depositDate": "2025-10-27",
#             "method": "check",
#             "paymentDescription": "",
#             "paymentMethodId": "",
#             "provider": "null",
#             "token": "null",
#             "totalCollected": "20",
#         },
#         "posting": {
#             "claimId": "Q2xhaW1UeXBlOjE=",
#             "description": "",
#             "payerId": "Q2xhaW1Db3ZlcmFnZVR5cGU6MQ==",
#         },
#     },
# }


class Method(Enum):
    """Methods."""

    CASH = "cash"
    CHECK = "check"
    CARD = "card"
    OTHER = "other"


@dataclass
class LineItemTransaction:
    """Data for creating a line item transaction on a CoverageClaimPayment."""

    adjustment: Decimal
    adjustment_code: str
    allowed: Decimal
    claim_line_item_id: str | UUID
    payment: Decimal
    transfer_to: str | UUID
    write_off: bool

    def to_dict(self) -> dict[str, Any]:
        """Convert dataclass to dictionary."""
        return {
            "adjustment": self.adjustment,
            "adjustment_code": self.adjustment_code,
            "allowed": self.allowed,
            "claim_line_item_id": self.claim_line_item_id,
            "payment": self.payment,
            "transfer_to": self.transfer_to,
            "write_off": self.write_off,
        }


class PostCoverageClaimPayment(_BaseEffect):
    """
    An Effect that posts a coverage payment to a claim.
    """

    class Meta:
        effect_type = EffectType.POST_CLAIM_PAYMENT

    claim_id: str | UUID
    payer_id: str | UUID
    posting_description: str

    check_date: date
    check_number: str
    deposit_date: date
    method: Method
    payment_description: str
    total_collected: Decimal

    line_item_transactions: list[LineItemTransaction]

    @property
    def values(self) -> dict[str, Any]:
        """The values for the payload."""
        return {
            "posting": {
                "claim_id": str(self.claim_id),
                "payer_id": str(self.payer_id),
                "description": self.posting_description,
            },
            "payment_collection": {
                "check_date": self.check_date,
                "check_number": self.check_number,
                "deposit_date": self.deposit_date,
                "method": self.method,
                "payment_description": self.payment_description,
                "total_collected": self.total_collected,
            },
            "line_item_transactions": [t.to_dict() for t in self.line_item_transactions],
        }

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"data": self.values}

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

        if not claim.coverages.active().filter(id=self.payer_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    "Payer is not active for this claim",
                    self.payer_id,
                )
            )

        return errors


__exports__ = ("PostClaimPayment",)
