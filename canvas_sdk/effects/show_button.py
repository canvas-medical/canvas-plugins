from typing import Any

from pydantic import Field

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.base import _BaseEffect


class ShowButtonEffect(_BaseEffect):
    """
    An Effect that will decide an action button's properties.
    """

    class Meta:
        effect_type = EffectType.SHOW_ACTION_BUTTON

    key: str = Field(min_length=1)
    title: str = Field(min_length=1)
    priority: int = Field(default=0)

    @property
    def values(self) -> dict[str, Any]:
        """The ShowButtonEffect's values."""
        return {"key": self.key, "title": self.title, "priority": self.priority}

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"data": self.values}


__exports__ = ("ShowButtonEffect",)
