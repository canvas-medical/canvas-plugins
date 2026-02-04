from __future__ import annotations

from typing import NamedTuple


class Credentials(NamedTuple):
    """Credentials for S3 access.

    Attributes:
        key: AWS access key ID
        secret: AWS secret access key
        region: AWS region (e.g., 'us-east-1')
        bucket: S3 bucket name
    """

    key: str
    secret: str
    region: str
    bucket: str


__exports__ = ("Credentials",)
