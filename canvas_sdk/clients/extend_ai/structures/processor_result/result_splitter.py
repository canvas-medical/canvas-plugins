from dataclasses import dataclass
from typing import Self

from canvas_sdk.clients.extend_ai.structures.processor_result.split import Split
from canvas_sdk.clients.extend_ai.structures.structure import Structure


@dataclass(frozen=True)
class ResultSplitter(Structure):
    """Result of a splitter processor execution.

    Attributes:
        splits: List of document splits identified by the splitter processor.
    """

    splits: list[Split]

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create a ResultSplitter instance from a dictionary.

        Args:
            data: Dictionary containing splitter result data from the API.

        Returns:
            A new ResultSplitter instance.
        """
        return cls(splits=[Split.from_dict(item) for item in data["splits"]])

    def to_dict(self) -> dict:
        """Convert this ResultSplitter to a dictionary.

        Returns:
            Dictionary representation suitable for API requests.
        """
        return {
            "splits": [split.to_dict() for split in self.splits],
        }


__exports__ = ()
