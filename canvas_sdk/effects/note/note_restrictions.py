from typing import Any

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.base import _BaseEffect


class NoteRestrictionsEffect(_BaseEffect):
    """
    An effect that restricts access to a note for the requesting user.

    Return this effect from a handler responding to the GET_NOTE_RESTRICTIONS event to
    control whether a note is restricted for the requesting user, whether its content
    should be blurred, and what banner message should be displayed.
    """

    class Meta:
        effect_type = EffectType.NOTE_RESTRICTIONS

    restrict_access: bool = False
    blur_content: bool = False
    banner_message: str | None = None

    @property
    def values(self) -> dict[str, Any]:
        """Values for the effect."""
        return {
            "restrict_access": self.restrict_access,
            "blur_content": self.blur_content,
            "banner_message": self.banner_message,
        }


__exports__ = ("NoteRestrictionsEffect",)
