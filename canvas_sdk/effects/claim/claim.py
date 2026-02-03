from datetime import date
from typing import Literal
from uuid import UUID

from canvas_sdk.base import Model
from canvas_sdk.effects import Effect
from canvas_sdk.effects.claim.claim_comment import _AddClaimComment
from canvas_sdk.effects.claim.claim_label import ColorEnum, Label, _AddClaimLabel, _RemoveClaimLabel
from canvas_sdk.effects.claim.claim_queue import _MoveClaimToQueue
from canvas_sdk.effects.claim.payment.base import (
    ClaimAllocation,
    LineItemTransaction,
    PaymentMethod,
)
from canvas_sdk.effects.claim.payment.claim_payment import _PostClaimPayment


class ClaimEffect(Model):
    """
    Effect for performing actions on a Claim.

    Attributes:
        claim_id (UUID | str): The unique identifier for the claim instance.
    """

    claim_id: UUID | str

    def add_comment(self, comment: str) -> Effect:
        """
        Adds a comment to the claim.

        Args:
            comment (str): The comment text to add to the claim.

        Returns:
            Effect: An effect that adds the comment to the claim.
        """
        return _AddClaimComment(claim_id=self.claim_id, comment=comment).apply()

    def add_labels(self, labels: list[str | Label]) -> Effect:
        """
        Adds one or more labels to the claim.

        Args:
            labels (list[str | Label]): A list of label names (str) or Label objects with color and name.

        Returns:
            Effect: An effect that adds the labels to the claim.
        """
        return _AddClaimLabel(claim_id=self.claim_id, labels=labels).apply()

    def remove_labels(self, labels: list[str]) -> Effect:
        """
        Removes one or more labels from the claim.

        Args:
            labels (list[str]): A list of label names to remove.

        Returns:
            Effect: An effect that removes the labels from the claim.
        """
        return _RemoveClaimLabel(claim_id=self.claim_id, labels=labels).apply()

    def move_to_queue(self, queue: str) -> Effect:
        """
        Moves the claim to a queue.

        Args:
            queue (str): The name of the queue to move the claim to.

        Returns:
            Effect: An effect that moves the claim to the specified queue.
        """
        return _MoveClaimToQueue(claim_id=self.claim_id, queue=queue).apply()

    def post_payment(
        self,
        claim_coverage_id: str | UUID | Literal["patient"],
        line_item_transactions: list[LineItemTransaction],
        method: PaymentMethod,
        move_to_queue_name: str | None = None,
        claim_description: str | None = None,
        check_date: date | None = None,
        check_number: str | None = None,
        deposit_date: date | None = None,
        payment_description: str | None = None,
    ) -> Effect:
        """
        Posts a coverage or patient payment to the claim.

        Args:
            claim_coverage_id (str | UUID | Literal["patient"]): The coverage ID or "patient" for patient payments.
            line_item_transactions (list[LineItemTransaction]): The line item transactions for the payment.
            method (PaymentMethod): The payment method (CASH, CHECK, CARD, OTHER).
            move_to_queue_name (str | None): Optional queue name to move the claim to after posting.
            claim_description (str | None): Optional description for the claim allocation.
            check_date (date | None): Required when method is CHECK.
            check_number (str | None): Required when method is CHECK.
            deposit_date (date | None): Optional deposit date.
            payment_description (str | None): Optional payment description.

        Returns:
            Effect: An effect that posts the payment to the claim.
        """
        claim_allocation = ClaimAllocation(
            claim_id=self.claim_id,
            claim_coverage_id=claim_coverage_id,
            line_item_transactions=line_item_transactions,
            move_to_queue_name=move_to_queue_name,
            description=claim_description,
        )
        return _PostClaimPayment(
            claim=claim_allocation,
            method=method,
            check_date=check_date,
            check_number=check_number,
            deposit_date=deposit_date,
            payment_description=payment_description,
        ).apply()


__all__ = __exports__ = (
    "ClaimEffect",
    "Label",
    "ColorEnum",
    "LineItemTransaction",
    "PaymentMethod",
)
