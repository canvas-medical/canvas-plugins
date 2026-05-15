from dataclasses import dataclass
from typing import Self

from canvas_sdk.clients.extend_ai.constants.base_processor import BaseProcessor
from canvas_sdk.clients.extend_ai.constants.processor_type import ProcessorType
from canvas_sdk.clients.extend_ai.structures.config.advanced_options_extraction import (
    AdvancedOptionsExtraction,
)
from canvas_sdk.clients.extend_ai.structures.config.config_base import ConfigBase
from canvas_sdk.clients.extend_ai.structures.config.parser import Parser


@dataclass(frozen=True)
class ConfigExtraction(ConfigBase):
    """Configuration for an extraction processor.

    Attributes:
        base_processor: The base processor type to use (performance or light).
        extraction_rule: Custom rules to guide the extraction process.
        schema: The JSON schema defining the structure of extracted data.
        advanced_options: Advanced configuration options for extraction.
        parser: Parser configuration for document processing.
    """

    base_processor: BaseProcessor
    extraction_rule: str
    schema: dict
    advanced_options: AdvancedOptionsExtraction
    parser: Parser

    @classmethod
    def processor_type(cls) -> ProcessorType:
        """Get the processor type for this configuration.

        Returns:
            ProcessorType.EXTRACT for extraction processors.
        """
        return ProcessorType.EXTRACT

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create a ConfigExtraction instance from a dictionary.

        Args:
            data: Dictionary containing extraction configuration from the API.

        Returns:
            A new ConfigExtraction instance with defaults for missing values.
        """
        return cls(
            base_processor=BaseProcessor(data["baseProcessor"]),
            extraction_rule=data.get("extractionRule") or "",
            schema=data["schema"],
            advanced_options=AdvancedOptionsExtraction.from_dict(data["advancedOptions"]),
            parser=Parser.from_dict(data.get("parser") or {}),
        )

    def to_dict(self) -> dict:
        """Convert this ConfigExtraction to a dictionary.

        Returns:
            Dictionary representation suitable for API requests.
        """
        return {
            "type": ProcessorType.EXTRACT.value,
            "baseProcessor": self.base_processor.value,
            "extractionRule": self.extraction_rule,
            "schema": self.schema,
            "advancedOptions": self.advanced_options.to_dict(),
            "parser": self.parser.to_dict(),
        }


__exports__ = ()
