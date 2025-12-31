from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedHeader:
    """Represents a single email header from an inbound parsed email."""

    name: str
    value: str

    def to_dict(self) -> dict:
        """Convert parsed header to dictionary format."""
        return {
            "name": self.name,
            "value": self.value,
        }


__exports__ = ()
