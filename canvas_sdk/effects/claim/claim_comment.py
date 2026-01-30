from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect
from canvas_sdk.v1.data import Claim


class AddClaimComment(_BaseEffect):
    """Effect to add a comment to a Claim."""

    class Meta:
        effect_type = EffectType.ADD_CLAIM_COMMENT

    claim_id: UUID | str
    comment: str

    @property
    def values(self) -> dict[str, Any]:
        """The values for adding a claim comment."""
        return {"claim_id": str(self.claim_id), "comment": self.comment}

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        if not Claim.objects.filter(id=self.claim_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Claim with id {self.claim_id} does not exist.",
                    self.claim_id,
                )
            )
        return errors
