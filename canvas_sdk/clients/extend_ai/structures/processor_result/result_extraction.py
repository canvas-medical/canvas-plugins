from dataclasses import dataclass
from typing import Self

from canvas_sdk.clients.extend_ai.structures.structure import Structure


@dataclass(frozen=True)
class ResultExtraction(Structure):
    """Result of an extraction processor execution.

    Attributes:
        value: Dictionary containing the extracted data fields and their values.
    """

    value: dict

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create a ResultExtraction instance from a dictionary.

        Args:
            data: Dictionary containing extraction result data from the API.

        Returns:
            A new ResultExtraction instance.
        """
        return cls(value=data["value"])

    def to_dict(self) -> dict:
        """Convert this ResultExtraction to a dictionary.

        Returns:
            Dictionary representation suitable for API requests.
        """
        return {"value": self.value}


__exports__ = ()
