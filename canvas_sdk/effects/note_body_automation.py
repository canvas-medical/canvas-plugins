from typing import Any

from pydantic import Field

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.base import _BaseEffect


class ShowNoteBodyAutomationEffect(_BaseEffect):
    """
    An Effect that adds one entry to the note body automation list.

    The list is requested once per note load. The entry shows when the user
    types "/" in the note body, next to the native commands.
    """

    class Meta:
        effect_type = EffectType.SHOW_NOTE_BODY_AUTOMATION

    key: str = Field(min_length=1)
    title: str = Field(min_length=1)
    keywords: list[str] = []
    priority: int = Field(default=0)

    @property
    def values(self) -> dict[str, Any]:
        """The ShowNoteBodyAutomationEffect's values."""
        return {
            "key": self.key,
            "title": self.title,
            "keywords": self.keywords,
            "priority": self.priority,
        }


__exports__ = ("ShowNoteBodyAutomationEffect",)
