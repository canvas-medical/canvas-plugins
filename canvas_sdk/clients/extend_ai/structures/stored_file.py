from dataclasses import dataclass
from typing import Self

from canvas_sdk.clients.extend_ai.structures.structure import Structure


@dataclass(frozen=True)
class StoredFile(Structure):
    """Represents a file stored in Extend AI.

    Attributes:
        id: The unique identifier for the stored file.
        type: The MIME type or file type.
        name: The name of the file.
    """

    id: str
    type: str
    name: str

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create a StoredFile instance from a dictionary.

        Args:
            data: Dictionary containing file metadata from the API.

        Returns:
            A new StoredFile instance.
        """
        return cls(
            id=data["id"],
            type=data["type"],
            name=data["name"],
        )

    def to_dict(self) -> dict:
        """Convert this StoredFile to a dictionary.

        Returns:
            Dictionary representation suitable for API requests.
        """
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
        }


__exports__ = ()
