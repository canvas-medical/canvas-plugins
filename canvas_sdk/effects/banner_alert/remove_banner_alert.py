from typing import Any

from canvas_sdk.effects.base import EffectType, _BaseEffect


class RemoveBannerAlert(_BaseEffect):
    """
    An Effect that will remove/inactivate a banner alert in Canvas.
    """

    class Meta:
        effect_type = EffectType.REMOVE_BANNER_ALERT
        apply_required_fields = ("patient_id|patient_filter", "key")

    patient_id: str | None = None
    key: str | None = None

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"patient": self.patient_id, "patient_filter": self.patient_filter, "key": self.key}


__exports__ = ("RemoveBannerAlert",)
