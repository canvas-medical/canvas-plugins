from canvas_sdk.clients.sendgrid.structures.parsed_envelope import ParsedEnvelope
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Verify ParsedEnvelope is a frozen dataclass with correct fields."""
    tested = ParsedEnvelope
    fields = {
        "email_from": str,
        "email_to": list[str],
    }
    result = is_dataclass(tested, fields)
    expected = True
    assert result is expected


def test_from_dict() -> None:
    """Test creating ParsedEnvelope from dictionary."""
    tested = ParsedEnvelope
    data = {
        "from": "sender@example.com",
        "to": ["recipient1@example.com", "recipient2@example.com"],
    }
    result = tested.from_dict(data)
    expected = ParsedEnvelope(
        email_from="sender@example.com",
        email_to=["recipient1@example.com", "recipient2@example.com"],
    )
    assert result == expected


def test_to_dict() -> None:
    """Test converting ParsedEnvelope to dictionary."""
    tested = ParsedEnvelope(
        email_from="sender@example.com",
        email_to=["recipient@example.com"],
    )
    result = tested.to_dict()
    expected = {
        "emailFrom": "sender@example.com",
        "emailTo": ["recipient@example.com"],
    }
    assert result == expected
