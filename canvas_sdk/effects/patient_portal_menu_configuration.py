from enum import Enum
from typing import Any

from pydantic import Field

from canvas_sdk.effects.base import EffectType, _BaseEffect


class PatientPortalMenuConfiguration(_BaseEffect):
    """
    An Effect that will decide which menu items appear on the patient portal menu.
    """

    class Meta:
        effect_type = EffectType.SHOW_PATIENT_PORTAL_MENU_ITEMS

    class MenuItems(Enum):
        APPOINTMENTS = "appointments"
        MESSAGING = "messaging"
        MY_HEALTH = "my_health"
        PAYMENTS = "payments"
        LABS = "labs"
        CONTACT = "contact"
        RECORDS = "records"

    items: list[MenuItems] = Field(min_length=1)

    @property
    def values(self) -> dict[str, Any]:
        """The PatientPortalMenuConfiguration's values."""
        return {"items": [i.value for i in self.items]}

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"data": self.values}


__exports__ = ("PatientPortalMenuConfiguration",)
