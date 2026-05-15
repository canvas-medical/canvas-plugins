from dataclasses import dataclass
from typing import Self

from canvas_sdk.clients.extend_ai.structures.structure import Structure


@dataclass(frozen=True)
class Classification(Structure):
    """Represents a document classification result.

    Attributes:
        id: The unique identifier for this classification.
        type: The classification type or category.
        description: A description of the classification.
    """

    id: str
    type: str
    description: str

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create a Classification instance from a dictionary.

        Args:
            data: Dictionary containing classification data from the API.

        Returns:
            A new Classification instance.
        """
        return cls(
            id=data["id"],
            type=data["type"],
            description=data["description"],
        )

    def to_dict(self) -> dict:
        """Convert this Classification to a dictionary.

        Returns:
            Dictionary representation suitable for API requests.
        """
        return {
            "id": self.id,
            "type": self.type,
            "description": self.description,
        }


__exports__ = ()
