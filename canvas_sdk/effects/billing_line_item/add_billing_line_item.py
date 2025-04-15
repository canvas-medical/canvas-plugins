from typing import Any

from canvas_sdk.commands.constants import Coding
from canvas_sdk.effects.base import EffectType, _BaseEffect


class AddBillingLineItem(_BaseEffect):
    """
    An Effect that will result in a billing line item in a note footer.
    """

    class Meta:
        effect_type = EffectType.ADD_BILLING_LINE_ITEM
        apply_required_fields = ("note_id", "cpt")

    note_id: str | None = None
    cpt: str | None = None
    units: int | None = 1
    assessment_ids: list[str] = []
    modifiers: list[Coding] = []

    @property
    def values(self) -> dict[str, Any]:
        """The BillingLineItem's values."""
        return {
            "cpt": self.cpt,
            "units": self.units,
            "assessment_ids": self.assessment_ids,
            "modifiers": self.modifiers,
        }

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {
            "note_id": self.note_id,
            "data": self.values,
        }


__exports__ = ("AddBillingLineItem",)
