from typing import Any

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.base import _BaseEffect


class NoteRestrictionsUpdatedEffect(_BaseEffect):
    """
    Signal to the frontend that note permissions have changed and should be refetched.

    Return this from a handler after any action that affects the output of
    ``NoteRestrictionsEffect`` (e.g. writing a freeze key to NoteMetadata).
    home-app will broadcast a WebSocket notification so every connected client
    viewing that note refetches its permissions in real time.
    """

    class Meta:
        effect_type = EffectType.NOTE_RESTRICTIONS_UPDATED

    note_id: str

    @property
    def values(self) -> dict[str, Any]:
        """Values for the effect."""
        return {"note_id": self.note_id}


__exports__ = ("NoteRestrictionsUpdatedEffect",)
