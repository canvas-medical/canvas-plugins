from enum import StrEnum
from typing import Any

from canvas_sdk.effects import EffectType, _BaseEffect


class LaunchModelEffect(_BaseEffect):
    """An Effect that will launch a modal."""

    class Meta:
        effect_type = EffectType.LAUNCH_MODAL

    class TargetType(StrEnum):
        DEFAULT_MODAL = "default_modal"
        NEW_WINDOW = "new_window"
        RIGHT_CHART_PANE = "right_chart_pane"

    url: str
    target: TargetType = TargetType.DEFAULT_MODAL

    @property
    def values(self) -> dict[str, Any]:
        """The PatientChartSummaryConfiguration's values."""
        return {"url": self.url, "target": self.target.value}
