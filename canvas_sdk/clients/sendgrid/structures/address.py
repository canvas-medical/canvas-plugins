from dataclasses import dataclass


@dataclass(frozen=True)
class Address:
    """Represents an email address with name."""

    email: str
    name: str

    def to_dict(self) -> dict:
        """Convert address to dictionary format."""
        return {
            "email": self.email,
            "name": self.name,
        }


__exports__ = ()
