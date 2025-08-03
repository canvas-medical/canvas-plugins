from typing import Any

from canvas_sdk.base import Model
from canvas_sdk.effects.base import EffectType, _BaseEffect


class Group(Model):
    """
    Class representing a group of items in the Patient Chart.
    """

    items: list[Any]
    priority: int
    name: str

    def to_dict(self) -> dict[str, Any]:
        """Convert the Group object to a dictionary."""
        return {"items": self.items, "priority": self.priority, "name": self.name}


class PatientChartGroup(_BaseEffect):
    """
    An Effect that will send an invitation for the Patient Portal.
    """

    class Meta:
        effect_type = EffectType.PATIENT_CHART__GROUP_ITEMS

    items: dict[str, Group]

    @property
    def values(self) -> dict[str, Any]:
        """The user's id."""
        return {
            "items": [item.to_dict() for item in self.items.values() if isinstance(item, Group)]
        }

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"data": self.values}


__exports__ = (
    "PatientChartGroup",
    "Group",
)
