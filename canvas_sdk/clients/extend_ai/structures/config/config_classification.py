from dataclasses import dataclass
from typing import Self

from canvas_sdk.clients.extend_ai.constants.base_processor import BaseProcessor
from canvas_sdk.clients.extend_ai.constants.processor_type import ProcessorType
from canvas_sdk.clients.extend_ai.structures.classification import Classification
from canvas_sdk.clients.extend_ai.structures.config.advanced_options_classification import (
    AdvancedOptionsClassification,
)
from canvas_sdk.clients.extend_ai.structures.config.config_base import ConfigBase
from canvas_sdk.clients.extend_ai.structures.config.parser import Parser


@dataclass(frozen=True)
class ConfigClassification(ConfigBase):
    """Configuration for a classification processor.

    Attributes:
        classifications: List of possible classification categories.
        base_processor: The base processor type to use (performance or light).
        classification_rule: Custom rules to guide the classification.
        advanced_options: Advanced configuration options for classification.
        parser: Parser configuration for document processing.
    """

    classifications: list[Classification]
    base_processor: BaseProcessor
    classification_rule: str
    advanced_options: AdvancedOptionsClassification
    parser: Parser

    @classmethod
    def processor_type(cls) -> ProcessorType:
        """Get the processor type for this configuration.

        Returns:
            ProcessorType.CLASSIFY for classification processors.
        """
        return ProcessorType.CLASSIFY

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create a ConfigClassification instance from a dictionary.

        Args:
            data: Dictionary containing classification configuration from the API.

        Returns:
            A new ConfigClassification instance with defaults for missing values.
        """
        return cls(
            classifications=[Classification.from_dict(item) for item in data["classifications"]],
            base_processor=BaseProcessor(data["baseProcessor"]),
            classification_rule=data.get("classificationRules") or "",
            advanced_options=AdvancedOptionsClassification.from_dict(data["advancedOptions"]),
            parser=Parser.from_dict(data.get("parser") or {}),
        )

    def to_dict(self) -> dict:
        """Convert this ConfigClassification to a dictionary.

        Returns:
            Dictionary representation suitable for API requests.
        """
        return {
            "type": ProcessorType.CLASSIFY.value,
            "classifications": [item.to_dict() for item in self.classifications],
            "baseProcessor": self.base_processor.value,
            "classificationRules": self.classification_rule,
            "advancedOptions": self.advanced_options.to_dict(),
            "parser": self.parser.to_dict(),
        }


__exports__ = ()
