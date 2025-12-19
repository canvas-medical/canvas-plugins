from dataclasses import dataclass
from typing import Self

from canvas_sdk.clients.extend_ai.constants.parser_chunking import ParserChunking
from canvas_sdk.clients.extend_ai.constants.parser_target import ParserTarget
from canvas_sdk.clients.extend_ai.structures.structure import Structure


@dataclass(frozen=True)
class Parser(Structure):
    """Configuration for document parsing.

    Attributes:
        target: The target format for parsing (e.g., markdown, text).
        chunking_strategy: The strategy for chunking the document during parsing.
    """

    target: ParserTarget
    chunking_strategy: ParserChunking

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create a Parser instance from a dictionary.

        Args:
            data: Dictionary containing parser configuration from the API.

        Returns:
            A new Parser instance with defaults for missing values.
        """
        return cls(
            target=ParserTarget(data.get("target") or ParserTarget.MARKDOWN),
            chunking_strategy=ParserChunking(
                data.get("chunkingStrategy", {}).get("type") or ParserChunking.DOCUMENT
            ),
        )

    def to_dict(self) -> dict:
        """Convert this Parser to a dictionary.

        Returns:
            Dictionary representation suitable for API requests.
        """
        return {
            "target": self.target.value,
            "chunkingStrategy": {"type": self.chunking_strategy.value},
        }


__exports__ = ()
