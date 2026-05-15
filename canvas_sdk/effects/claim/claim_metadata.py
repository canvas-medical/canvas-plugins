from typing import Any
from uuid import UUID

from canvas_sdk.effects.metadata import BaseMetadata
from canvas_sdk.v1.data import Claim


class _ClaimMetadata(BaseMetadata):
    """Effect to upsert a Claim Metadata record."""

    class Meta:
        effect_type = "CLAIM_METADATA"

    claim_id: UUID | str

    def _get_error_details(self, method: Any) -> list:
        errors = super()._get_error_details(method)

        if not Claim.objects.filter(id=self.claim_id).exists():
            errors.append(
                self._create_error_detail(
                    "claim_id",
                    f"Claim with id: {self.claim_id} does not exist.",
                    self.claim_id,
                )
            )

        return errors


__exports__ = ()
