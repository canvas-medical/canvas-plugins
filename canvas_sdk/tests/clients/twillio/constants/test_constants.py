from canvas_sdk.clients.twillio.constants.constants import Constants, _Constants
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test _Constants dataclass has correct field types and default values."""
    tested = _Constants
    fields = {
        "sms_max_length": int,
        "standard_date": str,
        "twilio_date": str,
    }
    assert is_dataclass(tested, fields)

    assert tested.sms_max_length == 1600
    assert tested.standard_date == "%Y-%m-%dT%H:%M:%S%z"
    assert tested.twilio_date == "%a, %d %b %Y %H:%M:%S %z"

    assert isinstance(Constants, tested)
