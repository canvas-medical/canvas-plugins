from typing import Any

from canvas_sdk.effects.base import EffectType, _BaseEffect


class RemoveBannerAlert(_BaseEffect):
    """
    An Effect that will remove/inactivate a banner alert in Canvas.
    """

    class Meta:
        effect_type = EffectType.REMOVE_BANNER_ALERT

    patient_id: str
    key: str

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"patient": self.patient_id, "key": self.key}
