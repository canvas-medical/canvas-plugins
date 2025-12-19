from enum import Enum


class ParserTarget(Enum):
    """Target output formats for document parsing.

    MARKDOWN: Parse the document to markdown format.
    SPATIAL: Parse the document preserving spatial layout information.
    """

    MARKDOWN = "markdown"
    SPATIAL = "spatial"


__exports__ = ()
