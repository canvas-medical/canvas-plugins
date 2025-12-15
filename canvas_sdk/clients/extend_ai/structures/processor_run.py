from dataclasses import dataclass
from typing import Self

from canvas_sdk.clients.extend_ai.constants.processor_type import ProcessorType
from canvas_sdk.clients.extend_ai.constants.run_status import RunStatus
from canvas_sdk.clients.extend_ai.structures.processor_meta import ProcessorMeta
from canvas_sdk.clients.extend_ai.structures.processor_result import (
    ResultClassification,
    ResultExtraction,
    ResultSplitter,
)
from canvas_sdk.clients.extend_ai.structures.stored_file import StoredFile
from canvas_sdk.clients.extend_ai.structures.structure import Structure


@dataclass(frozen=True)
class ProcessorRun(Structure):
    """Represents a single execution of an Extend AI processor.

    Attributes:
        id: The unique identifier for the processor run.
        processor: Metadata about the processor that was executed.
        output: The output data produced by the processor run.
        status: The current status of the processor run.
        files: List of files associated with this processor run.
        usage: Total credit usage for this processor run.
    """

    id: str
    processor: ProcessorMeta
    output: ResultClassification | ResultExtraction | ResultSplitter | None
    status: RunStatus
    files: list[StoredFile]
    usage: int

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create a ProcessorRun instance from a dictionary.

        Args:
            data: Dictionary containing processor run data from the API.

        Returns:
            A new ProcessorRun instance with calculated total usage.
        """
        usage = [file.get("usage", {}).get("credits", 0) for file in data["files"]]
        usage.append(data.get("usage", {}).get("credits", 0))

        processor = ProcessorMeta(
            id=data["processorId"],
            name=data["processorName"],
            type=ProcessorType(data["type"]),
            created_at=None,
            updated_at=None,
        )
        status = RunStatus(data["status"])
        output: ResultClassification | ResultSplitter | ResultExtraction | None = None
        if status == RunStatus.PROCESSED:
            if processor.type == ProcessorType.CLASSIFY:
                output = ResultClassification.from_dict(data["output"])
            elif processor.type == ProcessorType.SPLITTER:
                output = ResultSplitter.from_dict(data["output"])
            else:  # if processor.type == ProcessorType.EXTRACT:
                output = ResultExtraction.from_dict(data["output"])

        return cls(
            id=data["id"],
            processor=processor,
            output=output,
            status=status,
            files=[StoredFile.from_dict(item) for item in data["files"]],
            usage=sum(usage),
        )

    def to_dict(self) -> dict:
        """Convert this ProcessorRun to a dictionary.

        Returns:
            Dictionary representation suitable for API requests.
        """
        output = None
        if self.output is not None:
            output = self.output.to_dict()
        return {
            "id": self.id,
            "processor": self.processor.to_dict(),
            "output": output,
            "status": self.status.value,
            "files": [f.to_dict() for f in self.files],
            "usage": self.usage,
        }


__exports__ = ()
