from enum import StrEnum
from typing import Any, Self

from pydantic import model_validator

from canvas_sdk.effects import EffectType, _BaseEffect


class LaunchModalEffect(_BaseEffect):
    """An Effect that will launch a modal."""

    class Meta:
        effect_type = EffectType.LAUNCH_MODAL

    class TargetType(StrEnum):
        DEFAULT_MODAL = "default_modal"
        NEW_WINDOW = "new_window"
        RIGHT_CHART_PANE = "right_chart_pane"
        RIGHT_CHART_PANE_LARGE = "right_chart_pane_large"

    url: str | None = None
    content: str | None = None
    target: TargetType = TargetType.DEFAULT_MODAL

    @property
    def values(self) -> dict[str, Any]:
        """The LaunchModalEffect values."""
        return {"url": self.url, "content": self.content, "target": self.target.value}

    @model_validator(mode="after")
    def check_mutually_exclusive_fields(self) -> Self:
        """Check that url and content are mutually exclusive."""
        if self.url is not None and self.content is not None:
            raise ValueError("'url' and 'content' are mutually exclusive")

        return self


__exports__ = ("LaunchModalEffect",)
