import json
from typing import Any

from canvas_sdk.base import Model
from canvas_sdk.effects import Effect, EffectType


class EventValidationError(Model):
    """
    Effect to abort an event, returned in response to a pre- event.

    Attributes:
        message (str): A descriptive error message.
    """

    class Meta:
        effect_type = EffectType.EVENT_VALIDATION_ERROR

    message: str

    @property
    def effect_payload(self) -> dict[str, Any]:
        """Payload to include in the Effect."""
        return {"message": self.message}

    def apply(self) -> Effect:
        """Applies the EventValidationError effect, which aborts the responded-to pre- event."""
        self._validate_before_effect("apply")
        return Effect(type=self.Meta.effect_type, payload=json.dumps(self.effect_payload))


__exports__ = ("EventValidationError",)
