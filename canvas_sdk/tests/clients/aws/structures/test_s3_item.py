from datetime import datetime

from canvas_sdk.clients.aws.structures.s3_item import S3Item
from canvas_sdk.tests.conftest import is_namedtuple


def test_class() -> None:
    """Test S3Item is a NamedTuple with correct fields and types."""
    assert is_namedtuple(
        S3Item,
        {
            "key": str,
            "size": int,
            "last_modified": datetime,
        },
    )
