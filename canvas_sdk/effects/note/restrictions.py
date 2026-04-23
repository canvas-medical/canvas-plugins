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


class NoteRestrictionsUpdatedEffect(_BaseEffect):
    """
    Signal to the frontend that note restrictions have changed and should be refetched.

    Return this from a handler after any action that affects the output of
    ``NoteRestrictionsEffect`` (e.g. writing a restriction key to NoteMetadata).
    home-app will broadcast a WebSocket notification so every connected client
    viewing that note refetches its restrictions in real time.
    """

    class Meta:
        effect_type = EffectType.NOTE_RESTRICTIONS_UPDATED

    note_id: str

    @property
    def values(self) -> dict[str, Any]:
        """Values for the effect."""
        return {"note_id": self.note_id}


__exports__ = ("NoteRestrictionsEffect", "NoteRestrictionsUpdatedEffect")
