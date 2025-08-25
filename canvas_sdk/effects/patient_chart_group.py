from typing import Any

from canvas_sdk.effects.base import EffectType, _BaseEffect
from canvas_sdk.effects.group import Group


class PatientChartGroup(_BaseEffect):
    """
    An Effect that groups chart items by name and priority.
    """

    class Meta:
        effect_type = EffectType.PATIENT_CHART__GROUP_ITEMS

    items: dict[str, Group]

    @property
    def values(self) -> dict[str, Any]:
        """The chart items."""
        return {
            "items": [item.to_dict() for item in self.items.values() if isinstance(item, Group)]
        }

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"data": self.values}


__exports__ = ("PatientChartGroup",)
