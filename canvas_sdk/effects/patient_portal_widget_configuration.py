from enum import Enum
from typing import Any

from pydantic import Field

from canvas_sdk.effects.base import EffectType, _BaseEffect


class PatientPortalWidgetConfiguration(_BaseEffect):
    """
    An Effect that will decide which widget items appear on the patient portal landing page.
    """

    class Meta:
        effect_type = EffectType.SHOW_PATIENT_PORTAL_WIDGET_ITEMS

    class WidgetItems(Enum):
        APPOINTMENTS = "appointments"
        MESSAGING = "messaging"

    items: list[WidgetItems] = Field(min_length=1)

    @property
    def values(self) -> dict[str, Any]:
        """The PatientPortalWidgetConfiguration's values."""
        return {"items": [i.value for i in self.items]}

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"data": self.values}
