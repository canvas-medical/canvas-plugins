from canvas_sdk.clients.aws.structures.credentials import Credentials
from canvas_sdk.tests.conftest import is_namedtuple


def test_class() -> None:
    """Test Credentials is a NamedTuple with correct fields and types."""
    assert is_namedtuple(
        Credentials,
        {
            "key": str,
            "secret": str,
            "region": str,
            "bucket": str,
        },
    )
