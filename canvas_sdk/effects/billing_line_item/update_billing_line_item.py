from typing import Any

from canvas_sdk.commands.constants import Coding
from canvas_sdk.effects.base import EffectType, _BaseEffect


class UpdateBillingLineItem(_BaseEffect):
    """
    An Effect that will update a billing line item in a note footer.
    """

    class Meta:
        effect_type = EffectType.UPDATE_BILLING_LINE_ITEM
        apply_required_fields = ("billing_line_item_id",)

    billing_line_item_id: str | None = None
    cpt: str | None = None
    units: int | None = None
    assessment_ids: list[str] | None = None
    modifiers: list[Coding] | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The BillingLineItem's values."""
        values: dict[str, str | int | list] = {}
        # only include the values where a value has been set so as to not unintentionally override existing values
        if self.cpt is not None:
            values["cpt"] = self.cpt
        if self.units is not None:
            values["units"] = self.units
        if self.assessment_ids is not None:
            values["assessment_ids"] = self.assessment_ids
        if self.modifiers is not None:
            values["modifiers"] = self.modifiers

        return values

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {
            "billing_line_item_id": self.billing_line_item_id,
            "data": self.values,
        }


__exports__ = ("UpdateBillingLineItem",)
