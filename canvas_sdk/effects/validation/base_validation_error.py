import json
from dataclasses import dataclass
from typing import Any, Self

from pydantic import Field

from canvas_sdk.base import Model
from canvas_sdk.effects import Effect, EffectType


@dataclass
class ValidationError:
    """
    Represents a validation error for an effect or command.

    Attributes:
        message: The validation error message to display
    """

    message: str

    def __post_init__(self) -> None:
        """
        Validate and normalize the error message after initialization.

        Raises:
            ValueError: If message is empty
        """
        if not self.message or not self.message.strip():
            raise ValueError("Error message cannot be empty")

        self.message = self.message.strip()

    def to_dict(self) -> dict[str, str]:
        """Convert the validation error to a dictionary."""
        return {"message": self.message}

    def __repr__(self) -> str:
        return f"ValidationError(message={self.message!r})"


class _BaseValidationErrorEffect(Model):
    """
    Abstract effect to abort an event.
    """

    class Meta:
        effect_type = EffectType.UNKNOWN_EFFECT

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
    def effect_payload(self) -> dict[str, Any]:
        """Payload to include in the Effect."""
        return {"errors": [error.to_dict() for error in self.errors]}

    def apply(self) -> Effect:
        """Applies the EventValidationError effect."""
        self._validate_before_effect("apply")
        return Effect(type=self.Meta.effect_type, payload=json.dumps(self.effect_payload))


__exports__ = ("ValidationError",)
