from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Any, Literal
from uuid import UUID

from django.db.models import QuerySet
from pydantic import Field
from pydantic.dataclasses import dataclass
from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import _BaseEffect
from canvas_sdk.v1.data import Claim, ClaimCoverage, ClaimLineItem, ClaimQueue


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

    check_date: date | None = None
    check_number: str | None = None
    deposit_date: date | None = None
    method: PaymentMethod
    payment_description: str | None = None

    @property
    def payment_collection_values(self) -> dict[str, Any]:
        """The values for the payment_collection."""
        return {
            "check_date": self.check_date.isoformat() if self.check_date else None,
            "check_number": self.check_number,
            "deposit_date": self.deposit_date.isoformat() if self.deposit_date else None,
            "method": self.method.value,
            "payment_description": self.payment_description,
        }

    def validate_payment_method_fields(self) -> list[InitErrorDetails]:
        """Checks that check_number and check_date are provided when method is 'check'."""
        if self.method != PaymentMethod.CHECK:
            return []
        errors = []
        if not self.check_number:
            errors.append(
                self._create_error_detail(
                    "value", "Check number is required for payment method CHECK", self.check_number
                )
            )
        if not self.check_date:
            errors.append(
                self._create_error_detail(
                    "value", "Check date is required for payment method CHECK", self.check_date
                )
            )
        return errors


@dataclass
class LineItemTransaction:
    """Data for creating a line item transaction on a ClaimPayment."""

    claim_line_item_id: str | UUID
    charged: Decimal | None = Field(decimal_places=2, default=None)
    allowed: Decimal | None = Field(decimal_places=2, default=None)
    payment: Decimal | None = Field(decimal_places=2, default=None)
    adjustment: Decimal | None = Field(decimal_places=2, default=None)
    adjustment_code: str | None = None
    transfer_remaining_balance_to: str | UUID | Literal["patient"] | None = None
    write_off: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert dataclass to dictionary."""
        return {
            "charged": str(self.charged) if self.charged is not None else None,
            "adjustment": str(self.adjustment) if self.adjustment is not None else None,
            "adjustment_code": self.adjustment_code,
            "allowed": str(self.allowed) if self.allowed is not None else None,
            "claim_line_item_id": str(self.claim_line_item_id),
            "payment": str(self.payment) if self.payment is not None else None,
            "transfer_to": str(self.transfer_remaining_balance_to)
            if self.transfer_remaining_balance_to
            else None,
            "write_off": self.write_off,
        }

    def is_first_transaction_for_line_item(
        self, line_item_transactions: list["LineItemTransaction"], index: int
    ) -> bool:
        """Returns True if this transaction is the first transaction for the claim line item, which can have many."""
        for i, lit in enumerate(line_item_transactions):
            if lit.claim_line_item_id == self.claim_line_item_id:
                return i == index
        return False

    def is_allowed_valid(self, is_patient_pmt: bool) -> list[tuple[str, str, Any]]:
        """Checks if allowed amount present on a patient payment."""
        if is_patient_pmt and self.allowed:
            return [self._format_error("Allowed amount should be $0 or None for patient postings")]
        return []

    def is_payment_required(
        self, is_first_transaction_for_line_item: bool
    ) -> list[tuple[str, str, Any]]:
        """Checks that the first transaction for a claim line item is either a payment or adjustment."""
        if (
            self.payment is None
            and is_first_transaction_for_line_item
            and self.adjustment is None
            and self.allowed is None
        ):
            return [
                self._format_error(
                    "Payment or adjustment is required for a claim line item's first transaction"
                )
            ]
        return []

    def is_adjustment_required(
        self, is_first_line_item_transaction: bool
    ) -> list[tuple[str, str, Any]]:
        """Checks that sequential transactions for a claim line item have an adjustment, and also checks if the adjustments have the correct corresponding fields."""
        errors = []

        if not is_first_line_item_transaction and not self.adjustment:
            errors.append(
                self._format_error(
                    "Specify an adjustment amount for added adjustments or remove the added adjustment line for this claim line item"
                )
            )
        if not self.adjustment and self.adjustment_code:
            errors.append(
                self._format_error("Enter an adjustment amount for the specified adjustment type")
            )
        if not self.adjustment and self.transfer_remaining_balance_to:
            errors.append(self._format_error("Enter an adjustment amount to transfer"))
        if not self.adjustment and self.write_off:
            errors.append(self._format_error("Enter an adjustment amount to write off"))

        return errors

    def is_adjustment_type_required(self) -> list[tuple[str, str, Any]]:
        """Checks if there is an adjustment without an adjustment code."""
        if self.adjustment and not self.adjustment_code:
            return [self._format_error("Specify an adjustment code for the adjustment amount")]
        return []

    def is_transfer_to_required(self) -> list[tuple[str, str, Any]]:
        """Checks if a transfer_to is required."""
        if not self.adjustment or not self.adjustment_code:
            return []
        adjustment_type = self.adjustment_code.split("-")
        # When "Transfer" adjustment group/code is selected a transfer destination is required.
        # This is the only group/code with this requirement.
        if (
            len(adjustment_type) < 2
            and not self.transfer_remaining_balance_to
            and adjustment_type[0] == "Transfer"
        ):
            return [self._format_error("Specify a payer to transfer the adjusted amount")]
        return []

    def is_adjustment_allowed(self, is_self_copay_line_item: bool) -> list[tuple[str, str, Any]]:
        """Checks if the adjustment is accurately formed."""
        errors = []

        if is_self_copay_line_item and any(
            [
                self.adjustment,
                self.adjustment_code,
                self.write_off,
                self.transfer_remaining_balance_to,
            ]
        ):
            errors.append(
                self._format_error("Adjustments and transfers not allowed for COPAY charges")
            )

        if self.adjustment and self.write_off and self.transfer_remaining_balance_to:
            errors.append(
                self._format_error(
                    "Adjustments cannot write off and transfer at the same time, please set write off=False or transfer_remaining_balance_to=None to create the posting"
                )
            )
        return errors

    def is_payer_valid(
        self, is_self_copay_line_item: bool, is_patient_pmt: bool
    ) -> list[tuple[str, str, Any]]:
        """Checks that payments made on a COPAY line item only come from a patient."""
        if is_self_copay_line_item and not is_patient_pmt:
            return [self._format_error("COPAY payments may only be posted by patients")]
        return []

    def is_transfer_to_valid(
        self,
        claim_coverage_id: str | UUID | Literal["patient"],
        claim_coverages: QuerySet[ClaimCoverage],
    ) -> list[tuple[str, str, Any]]:
        """Checks that transfers are not made to the same payer as the transaction payer and that the transfer_to field is a valid payer for the claim."""
        if not self.transfer_remaining_balance_to:
            return []

        if self.transfer_remaining_balance_to and str(self.transfer_remaining_balance_to) == str(
            claim_coverage_id
        ):
            return [self._format_error("Can't create transfers to same payer")]

        if (
            self.transfer_remaining_balance_to != "patient"
            and not claim_coverages.filter(id=self.transfer_remaining_balance_to).exists()
        ):
            return [
                self._format_error(
                    "Balance can only be transferred to patient or an active coverage for the claim"
                )
            ]
        return []

    def _format_error(self, error_message: str) -> tuple[str, str, Any]:
        return ("value", error_message, self.to_dict())

    def validate(
        self,
        line_item_transactions: list["LineItemTransaction"],
        index: int,
        claim_line_items: QuerySet[ClaimLineItem],
        claim_coverage_id: str | UUID | Literal["patient"],
        active_claim_coverages: QuerySet[ClaimCoverage],
    ) -> list[tuple[str, str, Any]]:
        """Returns error details for a line item transaction, using the context of other transactions for the claim."""
        if not (line_item := claim_line_items.filter(id=self.claim_line_item_id).first()):
            return [
                self._format_error(
                    "The provided claim_line_item_id does not correspond to an existing ClaimLineItem"
                )
            ]

        is_patient_pmt = claim_coverage_id == "patient"
        if errors := self.is_allowed_valid(is_patient_pmt):
            return errors

        is_first_transaction_for_line_item = self.is_first_transaction_for_line_item(
            line_item_transactions, index
        )
        if errors := self.is_payment_required(is_first_transaction_for_line_item):
            return errors
        if errors := self.is_adjustment_required(is_first_transaction_for_line_item):
            return errors

        if errors := self.is_adjustment_type_required():
            return errors
        if errors := self.is_transfer_to_required():
            return errors

        is_self_copay_line_item = line_item.proc_code == "COPAY"
        if errors := self.is_adjustment_allowed(is_self_copay_line_item):
            return errors
        if errors := self.is_payer_valid(is_self_copay_line_item, is_patient_pmt):
            return errors

        if errors := self.is_transfer_to_valid(claim_coverage_id, active_claim_coverages):
            return errors

        return []


@dataclass
class ClaimAllocation:
    """Claim payment details."""

    claim_id: str | UUID
    claim_coverage_id: str | UUID | Literal["patient"]
    line_item_transactions: list[LineItemTransaction]
    move_to_queue_name: str | None = None
    description: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert dataclass to dictionary."""
        return {
            "claim_id": str(self.claim_id),
            "claim_coverage_id": str(self.claim_coverage_id),
            "line_item_transactions": [lit.to_dict() for lit in self.line_item_transactions],
            "move_to_queue_name": self.move_to_queue_name,
            "description": self.description,
        }

    def validate_claim_coverage(
        self, active_claim_coverages: QuerySet[ClaimCoverage], payer_id: str | None = None
    ) -> str | None:
        """Checks that coverage is active, and if from ClaimsRemit that payer_id provided matches the coverage payer_id."""
        if not payer_id and self.claim_coverage_id == "patient":
            return None
        filters = {"id": self.claim_coverage_id} | ({} if not payer_id else {"payer_id": payer_id})
        if active_claim_coverages.filter(**filters):
            return None
        payer_id_message = f" with payer_id {payer_id}" if payer_id else ""
        return f"The provided claim_coverage_id does not correspond to an active coverage for the claim{payer_id_message}"

    def validate_move_to_queue_name(self) -> list[tuple[str, str, Any]]:
        """Checks that the queue to move to is a valid name."""
        if (
            not self.move_to_queue_name
            or ClaimQueue.objects.filter(name=self.move_to_queue_name).exists()
        ):
            return []
        return [
            (
                "value",
                "The provided move_to_queue_name does not correspond to an existing ClaimQueue",
                self.move_to_queue_name,
            )
        ]

    def validate_claim_id(self) -> Claim | None:
        """Checks that the claim exists."""
        return Claim.objects.filter(id=self.claim_id).first()

    def validate(self, payer_id: str | None = None) -> list[tuple[str, str, Any]]:
        """Returns error details for a claim allocation."""
        if not (claim := self.validate_claim_id()):
            claim_error = "The provided claim_id does not correspond with an existing Claim"
            return [("value", claim_error, str(self.claim_id))]
        active_claim_coverages = claim.coverages.active()
        if coverage_error := self.validate_claim_coverage(active_claim_coverages, payer_id):
            return [("value", coverage_error, {"claim_coverage_id": str(self.claim_coverage_id)})]

        errors = []
        errors.extend(self.validate_move_to_queue_name())
        for index, line_item_transaction in enumerate(self.line_item_transactions):
            errors.extend(
                line_item_transaction.validate(
                    self.line_item_transactions,
                    index,
                    claim.line_items.active(),
                    self.claim_coverage_id,
                    active_claim_coverages,
                )
            )
        return errors


__exports__ = (
    "PaymentMethod",
    "LineItemTransaction",
    "ClaimAllocation",
)
