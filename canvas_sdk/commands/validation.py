from typing import Any, Self

from pydantic import Field

from canvas_sdk.effects import EffectType, _BaseEffect
from canvas_sdk.utils.validation_error import ValidationError


class CommandValidationErrorEffect(_BaseEffect):
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

    errors: list[ValidationError] = Field(default_factory=list)

    def add_error(self, message: str | ValidationError) -> Self:
        """
        Add a validation error to the effect.

        This method allows incremental building of validation errors
        and supports method chaining.

        Args:
            message: The error message to display, or a ValidationError object

        Returns:
            Self for method chaining

        Raises:
            ValueError: If message is empty

        Example:
            effect = CommandValidationErrorEffect()
            effect.add_error("Narrative is required")
            effect.add_error("Dosage must be positive")

            # Using ValidationError objects
            error = ValidationError("Already validated error")
            effect.add_error(error)

            # Method chaining
            effect.add_error("Error 1").add_error("Error 2")
        """
        if isinstance(message, ValidationError):
            self.errors.append(message)
        else:
            error = ValidationError(message=message)
            self.errors.append(error)
        return self

    @property
    def values(self) -> dict[str, Any]:
        """
        Convert validation errors to the expected format.

        Returns:
        Dict with 'errors' key containing list of error dicts
        """
        return {"errors": [error.to_dict() for error in self.errors]}


__exports__ = (
    "CommandValidationErrorEffect",
    "ValidationError",
)
