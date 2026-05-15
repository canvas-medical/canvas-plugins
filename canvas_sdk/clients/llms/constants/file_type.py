from enum import Enum


class FileType(Enum):
    """Enumeration of supported file types for LLM file attachments.

    Attributes:
        IMAGE: Image file type (e.g., PNG, JPEG, GIF).
        PDF: PDF document file type.
        TEXT: Plain text file type.
    """

    IMAGE = "image"
    PDF = "pdf"
    TEXT = "text"


__exports__ = ()
