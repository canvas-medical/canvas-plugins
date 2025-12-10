import json
from typing import Any

from canvas_sdk.base import Model
from canvas_sdk.effects import Effect, EffectType


class NoteValidationError(Model):
    """
    Effect to abort the creation of a Note or Note-related entity, such as NoteStateChangeEvent.

    Attributes:
        message (str): A descriptive error message.
    """

    class Meta:
        effect_type = EffectType.NOTE_VALIDATION_ERROR

    message: str

    @property
    def effect_payload(self) -> dict[str, Any]:
        """Payload to include in the Effect."""
        return {"message": self.message}

    def apply(self) -> Effect:
        """Applies the NoteValidationError effect by returning the corresponding Effect object."""
        self._validate_before_effect("apply")
        return Effect(type=self.Meta.effect_type, payload=json.dumps(self.effect_payload))


__exports__ = ("NoteValidationError",)
