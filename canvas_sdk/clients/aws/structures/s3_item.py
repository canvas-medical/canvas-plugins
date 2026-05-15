from __future__ import annotations

from datetime import datetime
from typing import NamedTuple


class S3Item(NamedTuple):
    """S3 object metadata.

    Attributes:
        key: Object key (path) in the S3 bucket
        size: Object size in bytes
        last_modified: Timestamp of the last modification
    """

    key: str
    size: int
    last_modified: datetime


__exports__ = ("S3Item",)
