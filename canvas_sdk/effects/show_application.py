from typing import Any

from pydantic import Field

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.base import _BaseEffect


class ShowApplicationEffect(_BaseEffect):
    """An Effect that returns an application's properties."""

    class Meta:
        effect_type = EffectType.SHOW_APPLICATION

    name: str = Field(min_length=1)
    identifier: str = Field(min_length=1)
    open_by_default: bool = Field(default=False)
    priority: int = Field(default=0)

    @property
    def values(self) -> dict[str, Any]:
        """The ShowApplicationEffect's values."""
        return {
            "name": self.name,
            "identifier": self.identifier,
            "open_by_default": self.open_by_default,
            "priority": self.priority,
        }

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"data": self.values}


__exports__ = ("ShowApplicationEffect",)
