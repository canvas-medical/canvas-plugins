import pytest

from canvas_sdk.clients.twillio.structures.request_failed import RequestFailed


def test_class() -> None:
    """Test RequestFailed is a RuntimeError subclass."""
    tested = RequestFailed
    assert issubclass(tested, RuntimeError)


@pytest.mark.parametrize(
    ("status_code", "message"),
    [
        pytest.param(400, "Bad Request", id="bad_request"),
        pytest.param(401, "Unauthorized", id="unauthorized"),
        pytest.param(404, "Not Found", id="not_found"),
        pytest.param(500, "Internal Server Error", id="server_error"),
    ],
)
def test_init(status_code: int, message: str) -> None:
    """Test RequestFailed.__init__ sets status_code and message attributes."""
    result = RequestFailed(status_code, message)
    assert result.status_code == status_code
    assert result.message == message
    assert str(result) == message
