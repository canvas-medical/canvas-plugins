from dataclasses import dataclass
from datetime import datetime
from typing import Self

from canvas_sdk.clients.extend_ai.constants.processor_type import ProcessorType
from canvas_sdk.clients.extend_ai.structures.structure import Structure


@dataclass(frozen=True)
class ProcessorMeta(Structure):
    """Metadata for an Extend AI processor.

    Attributes:
        id: The unique identifier for the processor.
        name: The human-readable name of the processor.
        type: The type of processor (classification, extraction, or splitting).
        created_at: The timestamp when the processor was created.
        updated_at: The timestamp when the processor was last updated.
    """

    id: str
    name: str
    type: ProcessorType
    created_at: datetime | None
    updated_at: datetime | None

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create a ProcessorMeta instance from a dictionary.

        Args:
            data: Dictionary containing processor metadata from the API.

        Returns:
            A new ProcessorMeta instance.
        """
        return cls(
            id=data["id"],
            name=data["name"],
            type=ProcessorType(data["type"]),
            created_at=datetime.fromisoformat(data["createdAt"]),
            updated_at=datetime.fromisoformat(data["updatedAt"]),
        )

    def to_dict(self) -> dict:
        """Convert this ProcessorMeta to a dictionary.

        Returns:
            Dictionary representation suitable for API requests.
        """
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }


__exports__ = ()
