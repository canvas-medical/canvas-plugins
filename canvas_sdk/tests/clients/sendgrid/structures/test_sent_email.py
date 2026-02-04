from datetime import UTC, datetime

import pytest

from canvas_sdk.clients.sendgrid.constants.status_email import StatusEmail
from canvas_sdk.clients.sendgrid.structures.sent_email import SentEmail
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test SentEmail dataclass has correct field types."""
    tested = SentEmail
    fields = {
        "from_email": str,
        "message_id": str,
        "subject": str,
        "to_email": str,
        "reason": str,
        "status": StatusEmail,
        "created_at": datetime,
    }
    assert is_dataclass(tested, fields)


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param(
            {
                "from_email": "sender@example.com",
                "sg_message_id": "MSG123",
                "subject": "Test Email",
                "to_email": "recipient@example.com",
                "reason": "",
                "status": "delivered",
                "sg_message_id_created_at": "2025-12-15T10:30:00+00:00",
            },
            SentEmail(
                from_email="sender@example.com",
                message_id="MSG123",
                subject="Test Email",
                to_email="recipient@example.com",
                reason="",
                status=StatusEmail.DELIVERED,
                created_at=datetime(2025, 12, 15, 10, 30, 0, tzinfo=UTC),
            ),
            id="delivered_email",
        ),
        pytest.param(
            {
                "from_email": "sender@example.com",
                "sg_message_id": "MSG456",
                "subject": "Bounced Email",
                "to_email": "bad@example.com",
                "reason": "bounce",
                "status": "bounced",
                "sg_message_id_created_at": "2025-12-16T14:20:00+00:00",
            },
            SentEmail(
                from_email="sender@example.com",
                message_id="MSG456",
                subject="Bounced Email",
                to_email="bad@example.com",
                reason="bounce",
                status=StatusEmail.BOUNCED,
                created_at=datetime(2025, 12, 16, 14, 20, 0, tzinfo=UTC),
            ),
            id="bounced_email",
        ),
    ],
)
def test_from_dict(data: dict, expected: SentEmail) -> None:
    """Test SentEmail.from_dict creates instance from dictionary."""
    test = SentEmail
    result = test.from_dict(data)
    assert result == expected


@pytest.mark.parametrize(
    ("sent_email", "expected"),
    [
        pytest.param(
            SentEmail(
                from_email="sender@example.com",
                message_id="MSG123",
                subject="Test Email",
                to_email="recipient@example.com",
                reason="",
                status=StatusEmail.DELIVERED,
                created_at=datetime(2025, 12, 15, 10, 30, 0, tzinfo=UTC),
            ),
            {
                "from_email": "sender@example.com",
                "message_id": "MSG123",
                "subject": "Test Email",
                "to_email": "recipient@example.com",
                "reason": "",
                "status": "delivered",
                "created_at": "2025-12-15T10:30:00+00:00",
            },
            id="delivered_to_dict",
        ),
        pytest.param(
            SentEmail(
                from_email="sender@example.com",
                message_id="MSG456",
                subject="Bounced Email",
                to_email="bad@example.com",
                reason="bounce",
                status=StatusEmail.BOUNCED,
                created_at=datetime(2025, 12, 16, 14, 20, 0, tzinfo=UTC),
            ),
            {
                "from_email": "sender@example.com",
                "message_id": "MSG456",
                "subject": "Bounced Email",
                "to_email": "bad@example.com",
                "reason": "bounce",
                "status": "bounced",
                "created_at": "2025-12-16T14:20:00+00:00",
            },
            id="bounced_to_dict",
        ),
    ],
)
def test_to_dict(sent_email: SentEmail, expected: dict) -> None:
    """Test SentEmail.to_dict converts instance to dictionary."""
    result = sent_email.to_dict()
    assert result == expected
