from datetime import date
from typing import Literal
from uuid import UUID

from pydantic import NonNegativeInt

from canvas_sdk.base import Model
from canvas_sdk.effects import Effect
from canvas_sdk.effects.claim.claim_banner_alert import (
    BannerAlertIntent,
    _AddClaimBannerAlert,
    _RemoveClaimBannerAlert,
)
from canvas_sdk.effects.claim.claim_comment import _AddClaimComment
from canvas_sdk.effects.claim.claim_label import ColorEnum, Label, _AddClaimLabel, _RemoveClaimLabel
from canvas_sdk.effects.claim.claim_metadata import _ClaimMetadata
from canvas_sdk.effects.claim.claim_provider import (
    ClaimBillingProvider,
    ClaimFacility,
    ClaimOrderingProvider,
    ClaimProvider,
    ClaimReferringProvider,
    _UpdateClaimProvider,
)
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

    def update_provider(
        self,
        billing_provider: ClaimBillingProvider | None = None,
        provider: ClaimProvider | None = None,
        referring_provider: ClaimReferringProvider | None = None,
        ordering_provider: ClaimOrderingProvider | None = None,
        facility: ClaimFacility | None = None,
        delay_seconds: NonNegativeInt | None = None,
    ) -> Effect:
        """
        Updates provider information for the claim.

        Args:
            billing_provider (ClaimBillingProvider | None): Billing provider information.
            provider (ClaimProvider | None): Rendering or attending provider information.
            referring_provider (ClaimReferringProvider | None): Referring provider information.
            ordering_provider (ClaimOrderingProvider | None): Ordering provider information.
            facility (ClaimFacility | None): Facility information.
            delay_seconds (int | None): Optional number of seconds to delay the effect.

        Returns:
            Effect: An effect that updates provider information for the claim.
        """
        return _UpdateClaimProvider(
            claim_id=self.claim_id,
            billing_provider=billing_provider,
            provider=provider,
            referring_provider=referring_provider,
            ordering_provider=ordering_provider,
            facility=facility,
        ).apply(delay_seconds=delay_seconds)

    def upsert_metadata(
        self, key: str, value: str, delay_seconds: NonNegativeInt | None = None
    ) -> Effect:
        """
        Upserts a metadata record to the claim.

        Args:
            key (str): The key of the metadata.
            value (str): The value of the metadata.
            delay_seconds (int | None): Optional number of seconds to delay the effect.

        Returns:
            Effect: An effect that upserts the metadata record to the claim.
        """
        return _ClaimMetadata(claim_id=self.claim_id, key=key).upsert(
            value=value, delay_seconds=delay_seconds
        )

    def add_banner(
        self,
        key: str,
        narrative: str,
        intent: BannerAlertIntent,
        href: str | None = None,
        delay_seconds: NonNegativeInt | None = None,
    ) -> Effect:
        """
        Adds a banner alert to a claim.

        Args:
            key (str): A unique identifier for the banner alert.
            narrative (str): The text content to display in the banner.
            intent (BannerAlertIntent): The intent/severity level of the banner (info, warning, or alert).
            href (str | None): Optional URL link for the banner. Defaults to None.
            delay_seconds (int | None): Optional number of seconds to delay the effect.

        Returns:
            Effect: An effect that adds the banner alert to the claim.
        """
        return _AddClaimBannerAlert(
            claim_id=self.claim_id, key=key, narrative=narrative, intent=intent, href=href
        ).apply(delay_seconds=delay_seconds)

    def remove_banner(self, key: str, delay_seconds: NonNegativeInt | None = None) -> Effect:
        """
        Removes a banner alert from a claim.

        Args:
            key (str): A unique identifier for the banner alert.
            delay_seconds (int | None): Optional number of seconds to delay the effect.

        Returns:
            Effect: An effect that removes the banner alert from the claim.
        """
        return _RemoveClaimBannerAlert(claim_id=self.claim_id, key=key).apply(
            delay_seconds=delay_seconds
        )

    def add_comment(self, comment: str, delay_seconds: NonNegativeInt | None = None) -> Effect:
        """
        Adds a comment to the claim.

        Args:
            comment (str): The comment text to add to the claim.
            delay_seconds (int | None): Optional number of seconds to delay the effect.

        Returns:
            Effect: An effect that adds the comment to the claim.
        """
        return _AddClaimComment(claim_id=self.claim_id, comment=comment).apply(
            delay_seconds=delay_seconds
        )

    def add_labels(
        self, labels: list[str | Label], delay_seconds: NonNegativeInt | None = None
    ) -> Effect:
        """
        Adds one or more labels to the claim.

        Args:
            labels (list[str | Label]): A list of label names (str) or Label objects with color and name.
            delay_seconds (int | None): Optional number of seconds to delay the effect.

        Returns:
            Effect: An effect that adds the labels to the claim.
        """
        return _AddClaimLabel(claim_id=self.claim_id, labels=labels).apply(
            delay_seconds=delay_seconds
        )

    def remove_labels(
        self, labels: list[str], delay_seconds: NonNegativeInt | None = None
    ) -> Effect:
        """
        Removes one or more labels from the claim.

        Args:
            labels (list[str]): A list of label names to remove.
            delay_seconds (int | None): Optional number of seconds to delay the effect.

        Returns:
            Effect: An effect that removes the labels from the claim.
        """
        return _RemoveClaimLabel(claim_id=self.claim_id, labels=labels).apply(
            delay_seconds=delay_seconds
        )

    def move_to_queue(self, queue: str, delay_seconds: NonNegativeInt | None = None) -> Effect:
        """
        Moves the claim to a queue.

        Args:
            queue (str): The name of the queue to move the claim to.
            delay_seconds (int | None): Optional number of seconds to delay the effect.

        Returns:
            Effect: An effect that moves the claim to the specified queue.
        """
        return _MoveClaimToQueue(claim_id=self.claim_id, queue=queue).apply(
            delay_seconds=delay_seconds
        )

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
        delay_seconds: NonNegativeInt | None = None,
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
            delay_seconds (int | None): Optional number of seconds to delay the effect.

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
        ).apply(delay_seconds=delay_seconds)


__all__ = __exports__ = (
    "BannerAlertIntent",
    "ClaimEffect",
    "Label",
    "ColorEnum",
    "LineItemTransaction",
    "PaymentMethod",
    "ClaimBillingProvider",
    "ClaimFacility",
    "ClaimOrderingProvider",
    "ClaimProvider",
    "ClaimReferringProvider",
)
