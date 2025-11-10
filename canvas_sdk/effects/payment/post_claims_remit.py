import base64
import mimetypes
from dataclasses import dataclass
from typing import Any, Literal
from uuid import UUID

from django.db.models import QuerySet
from pydantic import FilePath
from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType
from canvas_sdk.effects.payment.base import LineItemTransaction, PaymentMethod, PostPaymentBase
from canvas_sdk.v1.data import Claim, ClaimCoverage


@dataclass
class ClaimAllocation:
    """Claim payment details for a claim within a remit."""

    claim_id: str | UUID
    line_item_transactions: list[LineItemTransaction]
    subscriber_number: str | None = None
    move_to_queue_name: str | None = None
    description: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert dataclass to dictionary."""
        return {
            "claim_id": str(self.claim_id),
            "subscriber_number": self.subscriber_number,
            "line_item_transactions": [lit.to_dict() for lit in self.line_item_transactions],
            "move_to_queue_name": self.move_to_queue_name,
            "description": self.description,
        }

    def check_payer_id(
        self, payer_id: str | UUID | Literal["patient"], claim_coverages: QuerySet[ClaimCoverage]
    ) -> list[tuple[str, str, Any]]:
        """Checks that the payer is either 'patient' or an active coverage for the claim."""
        if payer_id == "patient":
            return []
        coverages = claim_coverages.filter(payer_id=payer_id)
        if not coverages:
            return [
                (
                    "value",
                    f"No active coverage with payer_id {payer_id} for this claim",
                    {"claim_id": self.claim_id},
                )
            ]
        if coverages.count() > 1 and self.subscriber_number:
            coverages = coverages.filter(subscriber_number=self.subscriber_number)
            if not coverages.exists():
                return [
                    (
                        "value",
                        f"No active coverage with payer_id {payer_id} and subscriber_number {self.subscriber_number} for this claim",
                        {"claim_id": self.claim_id},
                    )
                ]
        return []

    def validate(
        self, payer_id: str | UUID | Literal["patient"], claim: Claim
    ) -> list[tuple[str, str, str]]:
        """Returns error details for a claim allocation."""
        claim_line_items = claim.line_items.active()
        claim_coverages = claim.coverages.active()

        if errors := self.check_payer_id(payer_id, claim_coverages):
            return errors

        for index, line_item_transaction in enumerate(self.line_item_transactions):
            if errors := line_item_transaction.validate(
                self.line_item_transactions, index, claim_line_items, payer_id, claim_coverages
            ):
                return errors

        return []


class PostClaimsRemit(PostPaymentBase):
    """
    An Effect that posts a claims remittance.
    """

    class Meta:
        effect_type = EffectType.POST_CLAIMS_REMIT

    era_document: FilePath | None = None
    claims_allocation: list[ClaimAllocation]

    @property
    def era_file(self) -> dict[str, str] | None:
        """The base64 encoded file contents."""
        if not self.era_document:
            return None
        with open(self.era_document, "rb") as fh:
            b64 = base64.b64encode(fh.read()).decode()
        content_type = mimetypes.guess_type(str(self.era_document))[0] or "application/octet-stream"
        return {
            "filename": self.era_document.name,
            "content_type": content_type,
            "base64": b64,
        }

    @property
    def values(self) -> dict[str, Any]:
        """The values for the payload."""
        return {
            "posting": {
                "payer_id": str(self.payer_id),
                "era_file": self.era_file,
            },
            "payment_collection": self.payment_collection_values,
            "claims_allocation": [c.to_dict() for c in self.claims_allocation],
        }

    def validate_payment_method(self) -> list[InitErrorDetails]:
        """Enforces that only Check or Other are chosen as payment method."""
        if self.method not in [PaymentMethod.CHECK, PaymentMethod.OTHER]:
            return [
                (
                    self._create_error_detail(
                        "value",
                        "Claims remits can only have payment method of 'check' or 'other'",
                        self.method.value,
                    )
                )
            ]
        return []

    def validate_claim_ids(
        self, claim_ids: list[str], claims: QuerySet[Claim]
    ) -> list[InitErrorDetails]:
        """Checks that all claim_ids provided correspond to an existing Claim."""
        if claims.count() == len(claim_ids):
            return []
        incorrect_claim_ids = set(claim_ids) - {str(e) for e in claims.values_list("id", flat=True)}
        return [
            (
                self._create_error_detail(
                    "value",
                    f"There are {len(incorrect_claim_ids)} claim_ids that do not correspond to an existing Claim",
                    ", ".join(incorrect_claim_ids),
                )
            )
        ]

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        errors.extend(self.validate_payment_method())
        errors.extend(self.validate_payment_method_fields())

        claim_ids = [str(c.claim_id) for c in self.claims_allocation]
        claims = Claim.objects.filter(id__in=claim_ids)
        errors.extend(self.validate_claim_ids(claim_ids, claims))

        for claim_allocation in self.claims_allocation:
            claim = claims.get(id=claim_allocation.claim_id)
            claim_errors = claim_allocation.validate(self.payer_id, claim)
            errors.extend([self._create_error_detail(*e) for e in claim_errors])

        return errors


__exports__ = (
    "PostClaimsRemit",
    "ClaimAllocation",
    "LineItemTransaction",
    "PaymentMethod",
)
