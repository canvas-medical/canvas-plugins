from canvas_sdk.clients.twilio.structures.capabilities import Capabilities
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test Capabilities dataclass has correct field types."""
    tested = Capabilities
    fields = {
        "fax": bool,
        "mms": bool,
        "sms": bool,
        "voice": bool,
    }
    assert is_dataclass(tested, fields)


def test_from_dict() -> None:
    """Test Capabilities.from_dict creates instance from dictionary."""
    tested = Capabilities
    result = tested.from_dict(
        {
            "fax": False,
            "mms": True,
            "sms": True,
            "voice": False,
        }
    )
    expected = Capabilities(fax=False, mms=True, sms=True, voice=False)
    assert result == expected


def test_to_dict() -> None:
    """Test Capabilities.to_dict converts instance to dictionary."""
    tested = Capabilities(fax=False, mms=True, sms=True, voice=False)
    result = tested.to_dict()
    expected = {
        "fax": False,
        "mms": True,
        "sms": True,
        "voice": False,
    }
    assert result == expected
