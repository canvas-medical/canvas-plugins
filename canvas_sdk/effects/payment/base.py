from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Any, Literal
from uuid import UUID

from pydantic import Field

from canvas_sdk.effects.base import _BaseEffect


class PaymentMethod(Enum):
    """PaymentMethods."""

    CASH = "cash"
    CHECK = "check"
    CARD = "card"
    OTHER = "other"


class PostPaymentBase(_BaseEffect):
    """
    An BaseEffect for posting payment(s) to claim(s).
    """

    payer_id: str | UUID | Literal["patient"]
    posting_description: str | None = None

    check_date: date | None = None
    check_number: str | None = None
    # ^ these two are required only if method == check
    deposit_date: date | None = None
    method: PaymentMethod
    payment_description: str | None = None
    total_collected: Decimal = Field(decimal_places=2, ge=Decimal("0.00"))

    @property
    def payment_collection_values(self) -> dict[str, Any]:
        """The values for the payment_collection."""
        return {
            "check_date": self.check_date.isoformat() if self.check_date else None,
            "check_number": self.check_number,
            "deposit_date": self.deposit_date.isoformat() if self.deposit_date else None,
            "method": self.method.value,
            "payment_description": self.payment_description,
            "total_collected": str(self.total_collected),
        }


@dataclass
class LineItemTransaction:
    """Data for creating a line item transaction on a ClaimPayment."""

    claim_line_item_id: str | UUID
    charged: Decimal | None = Field(decimal_places=2, ge=Decimal("0.00"), default=None)
    allowed: Decimal | None = Field(decimal_places=2, ge=Decimal("0.00"), default=None)
    payment: Decimal | None = Field(decimal_places=2, ge=Decimal("0.00"), default=None)
    adjustment: Decimal | None = Field(decimal_places=2, ge=Decimal("0.00"), default=None)
    adjustment_code: str | None = None
    transfer_remaining_balance_to: str | UUID | Literal["patient"] | None = None
    write_off: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert dataclass to dictionary."""
        return {
            "charged": str(self.charged),
            "adjustment": str(self.adjustment),
            "adjustment_code": self.adjustment_code,
            "allowed": str(self.allowed),
            "claim_line_item_id": self.claim_line_item_id,
            # must be valid claim_line_item_id
            "payment": str(self.payment),
            "transfer_to": self.transfer_remaining_balance_to,
            # can only be the patient or other active coverages on the claim
            "write_off": self.write_off,
        }
