from pydantic import Field

from canvas_sdk.effects.banner_alert.constants import (
    BannerAlertIntent,
    BannerAlertPlacement,
)
from canvas_sdk.effects.base import _BaseEffect


class BannerAlert(_BaseEffect):
    """
    An Effect that will result in a banner alert in Canvas.
    """

    class Meta:
        effect_type = "SHOW_BANNER_ALERT"

    narrative: str = Field(max_length=90)
    placements: list[BannerAlertPlacement] = Field(min_length=1)
    intents: list[BannerAlertIntent] = Field(min_length=1)

    @property
    def values(self) -> dict:
        """The BannerAlert's values."""
        return {
            "narrative": self.narrative,
            "placement": [p.value for p in self.placements],
            "intent": [i.value for i in self.intents],
        }
