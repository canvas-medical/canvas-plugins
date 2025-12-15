from dataclasses import dataclass
from typing import Self

from canvas_sdk.clients.extend_ai.structures.structure import Structure


@dataclass(frozen=True)
class PartRange(Structure):
    """Represents a range of pages or parts in a document.

    Attributes:
        start: The starting page or part number (inclusive).
        end: The ending page or part number (inclusive).
    """

    start: int
    end: int

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create a PartRange instance from a dictionary.

        Args:
            data: Dictionary containing part range data from the API.

        Returns:
            A new PartRange instance.
        """
        return cls(
            start=int(data["start"]),
            end=int(data["end"]),
        )

    def to_dict(self) -> dict:
        """Convert this PartRange to a dictionary.

        Returns:
            Dictionary representation suitable for API requests.
        """
        return {
            "start": self.start,
            "end": self.end,
        }


__exports__ = ()
