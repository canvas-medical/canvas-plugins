from canvas_sdk.clients.twilio.structures.settings import Settings
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test Settings dataclass has correct field types."""
    tested = Settings
    fields = {
        "account_sid": str,
        "key": str,
        "secret": str,
    }
    assert is_dataclass(tested, fields)
