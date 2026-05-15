from canvas_sdk.clients.sendgrid.structures.settings import Settings
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test Settings dataclass has correct field types."""
    tested = Settings
    fields = {
        "key": str,
    }
    assert is_dataclass(tested, fields)
