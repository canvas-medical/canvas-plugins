from typing import Any

from pydantic import Field

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.surface_entry import _SurfaceEntryEffect


class ShowButtonEffect(_SurfaceEntryEffect):
    """
    An Effect that will decide an action button's properties.
    """

    class Meta:
        effect_type = EffectType.SHOW_ACTION_BUTTON

    color: str | None = Field(min_length=7, max_length=7, default=None)
    background: str | None = Field(min_length=7, max_length=7, default=None)

    @property
    def values(self) -> dict[str, Any]:
        """The ShowButtonEffect's values."""
        return {**super().values, "color": self.color, "background": self.background}


__exports__ = ("ShowButtonEffect",)
