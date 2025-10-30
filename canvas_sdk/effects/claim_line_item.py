from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect
from canvas_sdk.v1.data import ClaimLineItem


class UpdateClaimLineItem(_BaseEffect):
    """
    An Effect that updates a Claim Line Item.
    """

    class Meta:
        effect_type = EffectType.UPDATE_CLAIM_LINE_ITEM

    claim_line_item_id: str | UUID
    charge: float | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The values for the payload."""
        if self.charge is None:
            return {}
        return {"charge": str(self.charge)}

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"data": self.values, "claim_line_item_id": str(self.claim_line_item_id)}

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if not ClaimLineItem.objects.filter(id=self.claim_line_item_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    "Claim Line Item does not exist",
                    self.claim_line_item_id,
                )
            )
        return errors


__exports__ = ("UpdateClaimLineItem",)
