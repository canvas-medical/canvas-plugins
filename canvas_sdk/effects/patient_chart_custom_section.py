from typing import Any

from canvas_sdk.effects.base import EffectType, _BaseEffect


class PatientChartCustomSection(_BaseEffect):
    """
    Patient chart custom section.
    """

    class Meta:
        effect_type = EffectType.PATIENT_CHART_SUMMARY__CUSTOM_SECTION

    url: str | None = None
    content: str | None = None

    @property
    def values(self) -> dict[str, Any]:
        """Values for the effect."""
        return {"url": self.url, "content": self.content}

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"data": self.values}


__exports__ = ("PatientChartCustomSection",)
