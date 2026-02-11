from dataclasses import dataclass


@dataclass(frozen=True)
class BodyContent:
    """Represents the body content of an email with MIME type."""

    type: str  # mime type
    value: str

    def to_dict(self) -> dict:
        """Convert body content to dictionary format."""
        return {
            "type": self.type,
            "value": self.value,
        }


__exports__ = ()
