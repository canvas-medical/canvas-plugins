from typing import Any

from django.db.models import QuerySet
from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType
from canvas_sdk.effects.payment.base import (
    ClaimAllocation,
    PaymentMethod,
    PostPaymentBase,
)
from canvas_sdk.v1.data import Claim, Transactor


class PostClaimsRemit(PostPaymentBase):
    """
    An Effect that posts a claims remittance.
    """

    class Meta:
        effect_type = EffectType.POST_CLAIMS_REMIT

    payer_id: str
    # TBD: figure out how we are going to handle files sent to home-app
    era_document: str | None = None
    claims_allocation: list[ClaimAllocation]

    @property
    def values(self) -> dict[str, Any]:
        """The values for the payload."""
        return {
            "posting": {
                "payer_id": self.payer_id,
                "era_document": self.era_document,
                "description": self.posting_description,
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
            self._create_error_detail(
                "value",
                f"There are {len(incorrect_claim_ids)} claim_ids that do not correspond to an existing Claim",
                ", ".join(incorrect_claim_ids),
            )
        ]

    def validate_payer_id(self) -> list[InitErrorDetails]:
        """Checks that the payer_is corresponds to an existing Transactor."""
        if not Transactor.objects.filter(payer_id=self.payer_id):
            return [
                self._create_error_detail(
                    "value",
                    "The provided payer_id does not correspond to an existing Transactor",
                    self.payer_id,
                )
            ]
        return []

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        errors.extend(self.validate_payer_id())
        errors.extend(self.validate_payment_method())
        errors.extend(self.validate_payment_method_fields())

        claim_ids = [str(c.claim_id) for c in self.claims_allocation]
        claims = Claim.objects.filter(id__in=claim_ids)
        errors.extend(self.validate_claim_ids(claim_ids, claims))

        for claim_allocation in self.claims_allocation:
            claim_errors = claim_allocation.validate(self.payer_id)
            errors.extend([self._create_error_detail(*e) for e in claim_errors])

        return errors


__exports__ = ()
