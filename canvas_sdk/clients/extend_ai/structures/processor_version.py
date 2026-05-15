from dataclasses import dataclass
from datetime import datetime
from typing import Self

from canvas_sdk.clients.extend_ai.constants.processor_type import ProcessorType
from canvas_sdk.clients.extend_ai.structures.config.config_classification import (
    ConfigClassification,
)
from canvas_sdk.clients.extend_ai.structures.config.config_extraction import ConfigExtraction
from canvas_sdk.clients.extend_ai.structures.config.config_splitter import ConfigSplitter
from canvas_sdk.clients.extend_ai.structures.processor_meta import ProcessorMeta
from canvas_sdk.clients.extend_ai.structures.structure import Structure


@dataclass(frozen=True)
class ProcessorVersion(Structure):
    """Represents a specific version of an Extend AI processor.

    Attributes:
        id: The unique identifier for this processor version.
        version: The version name (e.g., "draft", "v1", "published").
        description: A description of this processor version.
        processor: Metadata about the processor this version belongs to.
        config: The configuration for this processor version.
        created_at: The timestamp when this version was created.
        updated_at: The timestamp when this version was last updated.
    """

    id: str
    version: str
    description: str
    processor: ProcessorMeta
    config: ConfigClassification | ConfigExtraction | ConfigSplitter
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create a ProcessorVersion instance from a dictionary.

        Args:
            data: Dictionary containing processor version data from the API.

        Returns:
            A new ProcessorVersion instance with the appropriate config type.
        """
        processor_type = ProcessorType(data["processorType"])
        config: ConfigClassification | ConfigExtraction | ConfigSplitter
        if processor_type == ProcessorType.EXTRACT:
            config = ConfigExtraction.from_dict(data["config"])
        elif processor_type == ProcessorType.CLASSIFY:
            config = ConfigClassification.from_dict(data["config"])
        else:  # processor_type==ExtendProcessorType.SPLITTER
            config = ConfigSplitter.from_dict(data["config"])

        return cls(
            id=data["id"],
            version=data["version"],
            description=data.get("description") or "",
            processor=ProcessorMeta(
                id=data["processorId"],
                name=data["processorName"],
                type=processor_type,
                created_at=None,
                updated_at=None,
            ),
            config=config,
            created_at=datetime.fromisoformat(data["createdAt"]),
            updated_at=datetime.fromisoformat(data["updatedAt"]),
        )

    def to_dict(self) -> dict:
        """Convert this ProcessorVersion to a dictionary.

        Returns:
            Dictionary representation suitable for API requests.
        """
        return {
            "id": self.id,
            "version": self.version,
            "description": self.description,
            "processor": self.processor.to_dict(),
            "config": self.config.to_dict(),
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }


__exports__ = ()
