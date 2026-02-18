from dataclasses import dataclass
from typing import Self

from canvas_sdk.clients.extend_ai.structures.structure import Structure


@dataclass(frozen=True)
class Insight(Structure):
    """An insight extracted from a document classification.

    Attributes:
        type: The type or category of the insight.
        content: The text content of the insight.
    """

    type: str
    content: str

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create an Insight instance from a dictionary.

        Args:
            data: Dictionary containing insight data from the API.

        Returns:
            A new Insight instance.
        """
        return cls(
            type=data["type"],
            content=data["content"],
        )

    def to_dict(self) -> dict:
        """Convert this Insight to a dictionary.

        Returns:
            Dictionary representation suitable for API requests.
        """
        return {
            "type": self.type,
            "content": self.content,
        }


__exports__ = ()
