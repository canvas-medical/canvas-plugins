from dataclasses import dataclass
from typing import Self

from canvas_sdk.clients.extend_ai.structures.processor_result.insight import Insight
from canvas_sdk.clients.extend_ai.structures.structure import Structure


@dataclass(frozen=True)
class ResultClassification(Structure):
    """Result of a classification processor execution.

    Attributes:
        type: The classification type assigned to the document.
        confidence: The confidence score for this classification (0.0 to 1.0).
        insights: List of insights extracted during classification.
    """

    type: str
    confidence: float
    insights: list[Insight]

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create a ResultClassification instance from a dictionary.

        Args:
            data: Dictionary containing classification result data from the API.

        Returns:
            A new ResultClassification instance.
        """
        return cls(
            type=data["type"],
            confidence=float(data["confidence"]),
            insights=[Insight.from_dict(item) for item in data["insights"]],
        )

    def to_dict(self) -> dict:
        """Convert this ResultClassification to a dictionary.

        Returns:
            Dictionary representation suitable for API requests.
        """
        return {
            "type": self.type,
            "confidence": round(self.confidence, 2),
            "insights": [item.to_dict() for item in self.insights],
        }


__exports__ = ()
