from canvas_sdk.clients.extend_ai.structures.request_failed import RequestFailed
from canvas_sdk.tests.conftest import is_namedtuple


def test_class() -> None:
    """Test that RequestFailed is a NamedTuple with the expected field types."""
    tested = RequestFailed
    fields = {
        "status_code": int,
        "message": str,
    }
    assert is_namedtuple(tested, fields)


def test_to_dict() -> None:
    """Test RequestFailed.to_dict correctly serializes error information."""
    tested = RequestFailed(
        status_code=403,
        message="theMessage",
    )
    expected = {
        "statusCode": 403,
        "message": "theMessage",
    }
    assert tested.to_dict() == expected
