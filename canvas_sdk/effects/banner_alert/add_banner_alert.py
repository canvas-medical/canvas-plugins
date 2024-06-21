from enum import Enum
from typing import Any

from pydantic import Field

from canvas_sdk.effects.base import EffectType, _BaseEffect


class AddBannerAlert(_BaseEffect):
    """
    An Effect that will result in a banner alert in Canvas.
    """

    class Meta:
        effect_type = EffectType.ADD_BANNER_ALERT

    class Placement(Enum):
        CHART = "chart"
        TIMELINE = "timeline"
        APPOINTMENT_CARD = "appointment_card"
        SCHEDULING_CARD = "scheduling_card"
        PROFILE = "profile"

    class Intent(Enum):
        INFO = "info"
        WARNING = "warning"
        ALERT = "alert"

    patient_id: str
    key: str
    narrative: str = Field(max_length=90)
    placement: list[Placement] = Field(min_length=1)
    intent: Intent
    href: str | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The BannerAlert's values."""
        return {
            "narrative": self.narrative,
            "placement": [p.value for p in self.placement],
            "intent": self.intent.value,
            "href": self.href,
        }

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"patient": self.patient_id, "key": self.key, "data": self.values}
