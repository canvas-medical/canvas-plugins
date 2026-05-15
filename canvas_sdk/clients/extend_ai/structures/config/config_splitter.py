from dataclasses import dataclass
from typing import Self

from canvas_sdk.clients.extend_ai.constants.base_processor import BaseProcessor
from canvas_sdk.clients.extend_ai.constants.processor_type import ProcessorType
from canvas_sdk.clients.extend_ai.structures.classification import Classification
from canvas_sdk.clients.extend_ai.structures.config.advanced_options_splitter import (
    AdvancedOptionsSplitter,
)
from canvas_sdk.clients.extend_ai.structures.config.config_base import ConfigBase
from canvas_sdk.clients.extend_ai.structures.config.parser import Parser


@dataclass(frozen=True)
class ConfigSplitter(ConfigBase):
    """Configuration for a document splitting processor.

    Attributes:
        split_classifications: List of classification categories for split sections.
        base_processor: The base processor type to use (performance or light).
        split_rules: Custom rules to guide the document splitting process.
        advanced_options: Advanced configuration options for splitting.
        parser: Parser configuration for document processing.
    """

    split_classifications: list[Classification]
    base_processor: BaseProcessor
    split_rules: str
    advanced_options: AdvancedOptionsSplitter
    parser: Parser

    @classmethod
    def processor_type(cls) -> ProcessorType:
        """Get the processor type for this configuration.

        Returns:
            ProcessorType.SPLITTER for document splitting processors.
        """
        return ProcessorType.SPLITTER

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create a ConfigSplitter instance from a dictionary.

        Args:
            data: Dictionary containing splitter configuration from the API.

        Returns:
            A new ConfigSplitter instance with defaults for missing values.
        """
        return cls(
            split_classifications=[
                Classification.from_dict(item) for item in data["splitClassifications"]
            ],
            base_processor=BaseProcessor(data["baseProcessor"]),
            split_rules=data.get("splitRules") or "",
            advanced_options=AdvancedOptionsSplitter.from_dict(data["advancedOptions"]),
            parser=Parser.from_dict(data.get("parser") or {}),
        )

    def to_dict(self) -> dict:
        """Convert this ConfigSplitter to a dictionary.

        Returns:
            Dictionary representation suitable for API requests.
        """
        return {
            "type": ProcessorType.SPLITTER.value,
            "splitClassifications": [item.to_dict() for item in self.split_classifications],
            "baseProcessor": self.base_processor.value,
            "splitRules": self.split_rules,
            "advancedOptions": self.advanced_options.to_dict(),
            "parser": self.parser.to_dict(),
        }


__exports__ = ()
