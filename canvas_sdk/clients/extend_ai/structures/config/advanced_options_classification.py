from dataclasses import dataclass
from typing import Self

from canvas_sdk.clients.extend_ai.structures.config.part_range import PartRange
from canvas_sdk.clients.extend_ai.structures.structure import Structure


@dataclass(frozen=True)
class AdvancedOptionsClassification(Structure):
    """Advanced configuration options for classification processors.

    Attributes:
        advanced_multimodal_enabled: Whether to enable advanced multimodal processing.
        page_ranges: List of page ranges to process (empty list means all pages).
    """

    advanced_multimodal_enabled: bool
    page_ranges: list[PartRange]

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create an AdvancedOptionsClassification instance from a dictionary.

        Args:
            data: Dictionary containing advanced classification options from the API.

        Returns:
            A new AdvancedOptionsClassification instance with defaults for missing values.
        """
        return cls(
            advanced_multimodal_enabled=bool(data.get("advancedMultimodalEnabled") or False),
            page_ranges=[PartRange.from_dict(item) for item in data.get("page_ranges") or []],
        )

    def to_dict(self) -> dict:
        """Convert this AdvancedOptionsClassification to a dictionary.

        Returns:
            Dictionary representation suitable for API requests.
        """
        return {
            "advancedMultimodalEnabled": self.advanced_multimodal_enabled,
            "pageRanges": [item.to_dict() for item in self.page_ranges],
        }


__exports__ = ()
