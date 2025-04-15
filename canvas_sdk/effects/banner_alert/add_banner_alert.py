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
        apply_required_fields = (
            "patient_id|patient_filter",
            "key",
            "narrative",
            "placement",
            "intent",
        )

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

    patient_id: str | None = None
    key: str | None = None
    narrative: str | None = Field(max_length=90, default=None)
    placement: list[Placement] | None = Field(min_length=1, default=None)
    intent: Intent | None = None
    href: str | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The BannerAlert's values."""
        return {
            "narrative": self.narrative,
            "placement": [p.value for p in self.placement] if self.placement else None,
            "intent": self.intent.value if self.intent else None,
            "href": self.href,
        }

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {
            "patient": self.patient_id,
            "patient_filter": self.patient_filter,
            "key": self.key,
            "data": self.values,
        }


__exports__ = ("AddBannerAlert",)
