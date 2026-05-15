from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedEnvelope:
    """Represents the SMTP envelope information from an inbound parsed email."""

    email_from: str
    email_to: list[str]

    @classmethod
    def from_dict(cls, data: dict) -> "ParsedEnvelope":
        """Create ParsedEnvelope instance from dictionary."""
        return cls(
            email_from=data["from"],
            email_to=data["to"],
        )

    def to_dict(self) -> dict:
        """Convert parsed envelope to dictionary format."""
        return {
            "emailFrom": self.email_from,
            "emailTo": self.email_to,
        }


__exports__ = ()
