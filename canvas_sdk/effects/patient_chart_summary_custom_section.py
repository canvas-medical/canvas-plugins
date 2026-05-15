from typing import Any, Self

from pydantic import model_validator

from canvas_sdk.effects.base import EffectType, _BaseEffect


class PatientChartSummaryCustomSection(_BaseEffect):
    """
    Patient chart custom section.
    """

    class Meta:
        effect_type = EffectType.PATIENT_CHART_SUMMARY__CUSTOM_SECTION

    url: str | None = None
    content: str | None = None
    icon: str | None = None
    icon_url: str | None = None

    @model_validator(mode="after")
    def check_mutually_exclusive_fields(self) -> Self:
        """
        Check that exactly one of url/content is provided.
        Check that exactly one of icon/icon_url is provided.
        """
        if self.url is not None and self.content is not None:
            raise ValueError("'url' and 'content' are mutually exclusive")

        if self.url is None and self.content is None:
            raise ValueError("One of 'url' or 'content' must be provided")

        if self.icon is not None and self.icon_url is not None:
            raise ValueError("'icon' and 'icon_url' are mutually exclusive")

        if self.icon is None and self.icon_url is None:
            raise ValueError("One of 'icon' or 'icon_url' must be provided")

        return self

    @property
    def values(self) -> dict[str, Any]:
        """Values for the effect."""
        return {
            "url": self.url,
            "content": self.content,
            "icon": self.icon,
            "icon_url": self.icon_url,
        }

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"data": self.values}


__exports__ = ("PatientChartSummaryCustomSection",)
