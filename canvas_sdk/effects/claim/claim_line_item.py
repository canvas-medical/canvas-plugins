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
    linked_diagnosis_codes: list[str | UUID] | None = None
    charge: float | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The values for the payload."""
        v: dict[str, Any] = {}
        if self.charge is not None:
            v["charge"] = str(self.charge)
        if self.linked_diagnosis_codes is not None:
            v["linked_diagnosis_codes"] = [str(a) for a in self.linked_diagnosis_codes]
        return v

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"data": self.values, "claim_line_item_id": str(self.claim_line_item_id)}

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if not (item := ClaimLineItem.objects.filter(id=self.claim_line_item_id).first()):
            errors.append(
                self._create_error_detail(
                    "value",
                    "Claim Line Item does not exist",
                    self.claim_line_item_id,
                )
            )
            return errors
        if self.linked_diagnosis_codes is not None:
            existing_diags = item.diagnosis_codes.filter(
                id__in=self.linked_diagnosis_codes
            ).values_list("id", flat=True)
            incorrect_ids = set(self.linked_diagnosis_codes) - set(existing_diags)
            if incorrect_ids:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "The provided ClaimLineItemDiagnosis ids do not correspond to the claim line item",
                        incorrect_ids,
                    )
                )
        return errors
