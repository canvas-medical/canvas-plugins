from dataclasses import dataclass
from typing import Self

from canvas_sdk.clients.extend_ai.structures.config.part_range import PartRange
from canvas_sdk.clients.extend_ai.structures.structure import Structure


@dataclass(frozen=True)
class AdvancedOptionsExtraction(Structure):
    """Advanced configuration options for extraction processors.

    Attributes:
        model_reasoning_insights_enabled: Whether to include model reasoning insights.
        advanced_multimodal_enabled: Whether to enable advanced multimodal processing.
        citations_enabled: Whether to include citations in the extracted data.
        page_ranges: List of page ranges to process (empty list means all pages).
    """

    model_reasoning_insights_enabled: bool
    advanced_multimodal_enabled: bool
    citations_enabled: bool
    page_ranges: list[PartRange]

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create an AdvancedOptionsExtraction instance from a dictionary.

        Args:
            data: Dictionary containing advanced extraction options from the API.

        Returns:
            A new AdvancedOptionsExtraction instance with defaults for missing values.
        """
        return cls(
            model_reasoning_insights_enabled=bool(
                data.get("modelReasoningInsightsEnabled") or False
            ),
            advanced_multimodal_enabled=bool(data.get("advancedMultimodalEnabled") or False),
            citations_enabled=bool(data.get("citationsEnabled") or False),
            page_ranges=[PartRange.from_dict(item) for item in data.get("page_ranges") or []],
        )

    def to_dict(self) -> dict:
        """Convert this AdvancedOptionsExtraction to a dictionary.

        Returns:
            Dictionary representation suitable for API requests.
        """
        return {
            "modelReasoningInsightsEnabled": self.model_reasoning_insights_enabled,
            "advancedMultimodalEnabled": self.advanced_multimodal_enabled,
            "citationsEnabled": self.citations_enabled,
            "pageRanges": [item.to_dict() for item in self.page_ranges],
        }


__exports__ = ()
