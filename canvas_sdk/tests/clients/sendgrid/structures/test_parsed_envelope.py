import pytest

from canvas_sdk.clients.sendgrid.structures.parsed_envelope import ParsedEnvelope
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test ParsedEnvelope dataclass has correct field types."""
    tested = ParsedEnvelope
    fields = {
        "email_from": str,
        "email_to": list[str],
    }
    assert is_dataclass(tested, fields)


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param(
            {
                "from": "sender@example.com",
                "to": ["recipient1@example.com", "recipient2@example.com"],
            },
            ParsedEnvelope(
                email_from="sender@example.com",
                email_to=["recipient1@example.com", "recipient2@example.com"],
            ),
            id="multiple_recipients",  # not realistic
        ),
        pytest.param(
            {
                "from": "noreply@service.com",
                "to": ["user@example.org"],
            },
            ParsedEnvelope(
                email_from="noreply@service.com",
                email_to=["user@example.org"],
            ),
            id="single_recipient",
        ),
    ],
)
def test_from_dict(data: dict, expected: ParsedEnvelope) -> None:
    """Test ParsedEnvelope.from_dict creates instance from dictionary."""
    test = ParsedEnvelope
    result = test.from_dict(data)
    assert result == expected


@pytest.mark.parametrize(
    ("envelope", "expected"),
    [
        pytest.param(
            ParsedEnvelope(
                email_from="sender@example.com",
                email_to=["recipient1@example.com", "recipient2@example.com"],
            ),
            {
                "emailFrom": "sender@example.com",
                "emailTo": ["recipient1@example.com", "recipient2@example.com"],
            },
            id="multiple_recipients",  # not realistic
        ),
        pytest.param(
            ParsedEnvelope(
                email_from="admin@company.net",
                email_to=["support@company.net"],
            ),
            {
                "emailFrom": "admin@company.net",
                "emailTo": ["support@company.net"],
            },
            id="single_recipient",
        ),
    ],
)
def test_to_dict(envelope: ParsedEnvelope, expected: dict) -> None:
    """Test ParsedEnvelope.to_dict converts instance to dictionary."""
    result = envelope.to_dict()
    assert result == expected
