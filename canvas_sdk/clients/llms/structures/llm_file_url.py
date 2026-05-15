from typing import NamedTuple

from canvas_sdk.clients.llms.constants.file_type import FileType


class LlmFileUrl(NamedTuple):
    """Container for file URL and type information for LLM file attachments.

    Attributes:
        url: The URL where the file can be accessed.
        type: The type of file (image, PDF, or text).
    """

    url: str
    type: FileType


__exports__ = ()
