import base64
import mimetypes
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from pydantic import FilePath
from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType
from canvas_sdk.effects.payment.base import LineItemTransaction, PaymentMethod, PostPaymentBase
from canvas_sdk.v1.data import Claim


@dataclass
class ClaimAllocation:
    """Claim payment details for a claim within a remit."""

    claim_id: str | UUID
    line_item_transactions: list[LineItemTransaction]
    subscriber_id: str | None = None
    move_to_queue_name: str | None = None
    description: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert dataclass to dictionary."""
        return {
            "claim_id": str(self.claim_id),
            "subscriber_id": self.subscriber_id,
            "line_item_transactions": [lit.to_dict() for lit in self.line_item_transactions],
            "move_to_queue_name": self.move_to_queue_name,
            "description": self.description,
        }


class PostClaimsRemit(PostPaymentBase):
    """
    An Effect that posts a claims remittance.
    """

    class Meta:
        effect_type = EffectType.POST_CLAIMS_REMIT

    era_document: FilePath
    claims_allocation: list[ClaimAllocation]

    @property
    def values(self) -> dict[str, Any]:
        """The values for the payload."""
        with open(self.era_document, "rb") as fh:
            b64 = base64.b64encode(fh.read()).decode()
        content_type = mimetypes.guess_type(str(self.era_document))[0] or "application/octet-stream"
        return {
            "posting": {
                "payer_id": str(self.payer_id),
                "era_file": {
                    "filename": self.era_document.name,
                    "content_type": content_type,
                    "base64": b64,
                },
            },
            "payment_collection": self.payment_collection_values,
            "claims_allocation": [c.to_dict() for c in self.claims_allocation],
        }

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if self.method not in [PaymentMethod.CHECK, PaymentMethod.OTHER]:
            errors.append(
                self._create_error_detail(
                    "value",
                    "Claims remits must have payment method of 'check' or 'other'",
                    self.method.value,
                )
            )

        claim_ids = [str(c.claim_id) for c in self.claims_allocation]
        claims = Claim.objects.filter(id__in=claim_ids)
        if claims.count() < len(claim_ids):
            incorrect_claim_ids = set(claim_ids) - {
                str(e) for e in claims.values_list("externally_exposable_id", flat=True)
            }
            errors.append(
                self._create_error_detail(
                    "value",
                    f"There are {len(incorrect_claim_ids)} claim_ids without an existing Claim",
                    ", ".join(incorrect_claim_ids),
                )
            )

        # todo: more validation!

        return errors


__exports__ = (
    "PostClaimsRemit",
    "ClaimAllocation",
    "LineItemTransaction",
    "PaymentMethod",
)
