from enum import Enum


class VersionName(Enum):
    """Standard version names for processors.

    LATEST: The latest published version of the processor.
    DRAFT: The draft/working version of the processor.
    """

    LATEST = "latest"
    DRAFT = "draft"


__exports__ = ()
