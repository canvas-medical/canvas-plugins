from canvas_sdk.effects import EffectType
from canvas_sdk.effects.validation.base import (
    ValidationError,
    _BaseValidationErrorEffect,
)


class CommandValidationErrorEffect(_BaseValidationErrorEffect):
    """
    Effect to represent command validation errors.

    This effect allows plugins to return validation errors for commands,
    which will be displayed to users in the Canvas UI.

    Example:
        # Add validation errors
        effect = CommandValidationErrorEffect()
        effect.add_error("Narrative is required")
        effect.add_error("Dosage must be a positive number")
        return [effect.apply()]

        # Or initialize with errors
        errors = [
            ValidationError("Narrative is required"),
            ValidationError("This command cannot be submitted yet")
        ]
        effect = CommandValidationErrorEffect(errors=errors)
        return [effect.apply()]

        # Method chaining
        effect = CommandValidationErrorEffect()
        effect.add_error("Error 1").add_error("Error 2")
        return [effect.apply()]
    """

    class Meta:
        effect_type = EffectType.COMMAND_VALIDATION_ERRORS


__all__ = __exports__ = (
    "CommandValidationErrorEffect",
    "ValidationError",
)
