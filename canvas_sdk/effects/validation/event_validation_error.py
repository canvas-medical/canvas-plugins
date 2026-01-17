from canvas_sdk.effects import EffectType
from canvas_sdk.effects.validation.base import _BaseValidationErrorEffect


class EventValidationError(_BaseValidationErrorEffect):
    """
    Effect to abort an event, returned in response to a pre-event.
    """

    class Meta:
        effect_type = EffectType.EVENT_VALIDATION_ERROR


__exports__ = ("EventValidationError",)
