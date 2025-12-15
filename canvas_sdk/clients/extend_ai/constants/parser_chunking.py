from enum import Enum


class ParserChunking(Enum):
    """Strategies for chunking documents during parsing.

    PAGE: Process the document page by page.
    DOCUMENT: Process the entire document as a single unit.
    SECTION: Process the document by logical sections.
    """

    PAGE = "page"
    DOCUMENT = "document"
    SECTION = "section"


__exports__ = ()
