from dataclasses import dataclass
from typing import Self

from canvas_sdk.clients.extend_ai.constants.split_method import SplitMethod
from canvas_sdk.clients.extend_ai.structures.config.part_range import PartRange
from canvas_sdk.clients.extend_ai.structures.structure import Structure


@dataclass(frozen=True)
class AdvancedOptionsSplitter(Structure):
    """Advanced configuration options for document splitting processors.

    Attributes:
        split_identifier_rules: Custom rules for identifying split points.
        split_method: The method to use for splitting (high precision or standard).
        page_ranges: List of page ranges to process (empty list means all pages).
    """

    split_identifier_rules: str
    split_method: SplitMethod
    page_ranges: list[PartRange]

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create an AdvancedOptionsSplitter instance from a dictionary.

        Args:
            data: Dictionary containing advanced splitter options from the API.

        Returns:
            A new AdvancedOptionsSplitter instance with defaults for missing values.
        """
        return cls(
            split_identifier_rules=data.get("splitIdentifierRules") or "",
            split_method=SplitMethod(data.get("splitMethod") or SplitMethod.HIGH_PRECISION),
            page_ranges=[PartRange.from_dict(item) for item in data.get("page_ranges") or []],
        )

    def to_dict(self) -> dict:
        """Convert this AdvancedOptionsSplitter to a dictionary.

        Returns:
            Dictionary representation suitable for API requests.
        """
        return {
            "splitIdentifierRules": self.split_identifier_rules,
            "splitMethod": self.split_method.value,
            "pageRanges": [item.to_dict() for item in self.page_ranges],
        }


__exports__ = ()
