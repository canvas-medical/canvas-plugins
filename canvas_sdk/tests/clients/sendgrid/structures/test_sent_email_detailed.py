from datetime import UTC, datetime

import pytest

from canvas_sdk.clients.sendgrid.constants.event_email import EventEmail
from canvas_sdk.clients.sendgrid.constants.status_email import StatusEmail
from canvas_sdk.clients.sendgrid.structures.email_event import EmailEvent
from canvas_sdk.clients.sendgrid.structures.sent_email_detailed import SentEmailDetailed
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test SentEmailDetailed dataclass has correct field types."""
    tested = SentEmailDetailed
    fields = {
        "from_email": str,
        "message_id": str,
        "subject": str,
        "to_email": str,
        "status": StatusEmail,
        "events": list[EmailEvent],
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
                "status": "delivered",
                "events": [
                    {
                        "event": "processed",
                        "email": "recipient@example.com",
                        "sg_message_id": "MSG123",
                        "sg_event_id": "EVT1",
                        "timestamp": 1734259800,
                    },
                    {
                        "event": "delivered",
                        "email": "recipient@example.com",
                        "sg_message_id": "MSG123",
                        "sg_event_id": "EVT2",
                        "timestamp": 1734259805,
                        "response": "250 OK",
                    },
                ],
            },
            SentEmailDetailed(
                from_email="sender@example.com",
                message_id="MSG123",
                subject="Test Email",
                to_email="recipient@example.com",
                status=StatusEmail.DELIVERED,
                events=[
                    EmailEvent(
                        event=EventEmail.PROCESSED,
                        email="recipient@example.com",
                        message_id="MSG123",
                        event_id="EVT1",
                        on_datetime=datetime.fromtimestamp(1734259800),
                        reason="",
                        response="",
                        url="",
                        attempt=-1,
                    ),
                    EmailEvent(
                        event=EventEmail.DELIVERED,
                        email="recipient@example.com",
                        message_id="MSG123",
                        event_id="EVT2",
                        on_datetime=datetime.fromtimestamp(1734259805),
                        reason="",
                        response="250 OK",
                        url="",
                        attempt=-1,
                    ),
                ],
            ),
            id="delivered_with_events",
        ),
    ],
)
def test_from_dict(data: dict, expected: SentEmailDetailed) -> None:
    """Test SentEmailDetailed.from_dict creates instance from dictionary."""
    test = SentEmailDetailed
    result = test.from_dict(data)
    assert result == expected


@pytest.mark.parametrize(
    ("email_detailed", "expected"),
    [
        pytest.param(
            SentEmailDetailed(
                from_email="sender@example.com",
                message_id="MSG123",
                subject="Test Email",
                to_email="recipient@example.com",
                status=StatusEmail.DELIVERED,
                events=[
                    EmailEvent(
                        event=EventEmail.DELIVERED,
                        email="recipient@example.com",
                        message_id="MSG123",
                        event_id="EVT123",
                        on_datetime=datetime(2025, 12, 15, 10, 30, 0, tzinfo=UTC),
                        reason="",
                        response="250 OK",
                        url="",
                        attempt=-1,
                    ),
                ],
            ),
            {
                "fromEmail": "sender@example.com",
                "messageDd": "MSG123",
                "subject": "Test Email",
                "toEmail": "recipient@example.com",
                "status": "delivered",
                "events": [
                    {
                        "event": "delivered",
                        "email": "recipient@example.com",
                        "messageId": "MSG123",
                        "eventId": "EVT123",
                        "datetime": "2025-12-15T10:30:00+00:00",
                        "reason": "",
                        "response": "250 OK",
                        "url": "",
                        "attempt": -1,
                    },
                ],
            },
            id="to_dict_with_events",
        ),
    ],
)
def test_to_dict(email_detailed: SentEmailDetailed, expected: dict) -> None:
    """Test SentEmailDetailed.to_dict converts instance to dictionary."""
    result = email_detailed.to_dict()
    assert result == expected
