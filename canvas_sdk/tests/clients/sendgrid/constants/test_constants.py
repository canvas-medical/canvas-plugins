from canvas_sdk.clients.sendgrid.constants.constants import Constants, _Constants
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test _Constants dataclass has correct field types and default values."""
    tested = _Constants
    fields = {
        "rfc3339_format": str,
    }
    assert is_dataclass(tested, fields)

    assert tested.rfc3339_format == "%Y-%m-%dT%H:%M:%SZ"

    assert isinstance(Constants, tested)
