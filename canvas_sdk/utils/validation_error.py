from dataclasses import dataclass


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
