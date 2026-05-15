from typing import NamedTuple


class FileContent(NamedTuple):
    """Container for file content with MIME type information.

    Attributes:
        mime_type: The MIME type of the file content (e.g., "application/pdf", "image/png").
        content: The file content as bytes, typically base64-encoded for API transmission.
    """

    mime_type: str
    content: bytes
    size: int


__exports__ = ()
