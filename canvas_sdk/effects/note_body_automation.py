from typing import Any

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.surface_entry import _SurfaceEntryEffect


class ShowNoteBodyAutomationEffect(_SurfaceEntryEffect):
    """
    An Effect that adds one entry to the note body automation list.

    The list is requested once per note load. The entry shows when the user
    types "/" in the note body, next to the native commands.
    """

    class Meta:
        effect_type = EffectType.SHOW_NOTE_BODY_AUTOMATION

    keywords: list[str] = []

    @property
    def values(self) -> dict[str, Any]:
        """The ShowNoteBodyAutomationEffect's values."""
        return {**super().values, "keywords": self.keywords}


__exports__ = ("ShowNoteBodyAutomationEffect",)
