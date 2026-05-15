from datetime import UTC, datetime

import pytest

from canvas_sdk.clients.sendgrid.constants.event_email import EventEmail
from canvas_sdk.clients.sendgrid.structures.email_event import EmailEvent
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test EmailEvent dataclass has correct field types."""
    tested = EmailEvent
    fields = {
        "event": EventEmail,
        "email": str,
        "message_id": str,
        "event_id": str,
        "on_datetime": datetime,
        "reason": str,
        "response": str,
        "url": str,
        "attempt": int,
    }
    assert is_dataclass(tested, fields)


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param(
            {
                "event": "delivered",
                "email": "test@example.com",
                "sg_message_id": "MSG123",
                "sg_event_id": "EVT123",
                "timestamp": 1734259800,
                "response": "250 OK",
            },
            EmailEvent(
                event=EventEmail.DELIVERED,
                email="test@example.com",
                message_id="MSG123",
                event_id="EVT123",
                on_datetime=datetime.fromtimestamp(1734259800),
                reason="",
                response="250 OK",
                url="",
                attempt=-1,
            ),
            id="delivered_event",
        ),
        pytest.param(
            {
                "event": "bounce",
                "email": "bad@example.com",
                "sg_message_id": "MSG456",
                "sg_event_id": "EVT456",
                "timestamp": 1734346800,
                "reason": "Invalid recipient",
            },
            EmailEvent(
                event=EventEmail.BOUNCE,
                email="bad@example.com",
                message_id="MSG456",
                event_id="EVT456",
                on_datetime=datetime.fromtimestamp(1734346800),
                reason="Invalid recipient",
                response="",
                url="",
                attempt=-1,
            ),
            id="bounce_event",
        ),
        pytest.param(
            {
                "event": "received",
                "recv_msgid": "RECV789",
                "sg_event_id": "EVT789",
                "timestamp": 1734433200,
            },
            EmailEvent(
                event=EventEmail.RECEIVED,
                email="",
                message_id="RECV789",
                event_id="EVT789",
                on_datetime=datetime.fromtimestamp(1734433200),
                reason="",
                response="",
                url="",
                attempt=-1,
            ),
            id="received_event",
        ),
        pytest.param(
            {
                "event": "click",
                "email": "user@example.com",
                "sg_message_id": "MSG999",
                "sg_event_id": "EVT999",
                "timestamp": 1734519600,
                "url": "https://example.com/link",
            },
            EmailEvent(
                event=EventEmail.CLICK,
                email="user@example.com",
                message_id="MSG999",
                event_id="EVT999",
                on_datetime=datetime.fromtimestamp(1734519600),
                reason="",
                response="",
                url="https://example.com/link",
                attempt=-1,
            ),
            id="click_event",
        ),
    ],
)
def test_from_dict(data: dict, expected: EmailEvent) -> None:
    """Test EmailEvent.from_dict creates instance from dictionary."""
    test = EmailEvent
    result = test.from_dict(data)
    assert result == expected


@pytest.mark.parametrize(
    ("event", "expected"),
    [
        pytest.param(
            EmailEvent(
                event=EventEmail.DELIVERED,
                email="test@example.com",
                message_id="MSG123",
                event_id="EVT123",
                on_datetime=datetime(2025, 12, 15, 10, 30, 0, tzinfo=UTC),
                reason="",
                response="250 OK",
                url="",
                attempt=-1,
            ),
            {
                "event": "delivered",
                "email": "test@example.com",
                "messageId": "MSG123",
                "eventId": "EVT123",
                "datetime": "2025-12-15T10:30:00+00:00",
                "reason": "",
                "response": "250 OK",
                "url": "",
                "attempt": -1,
            },
            id="delivered_to_dict",
        ),
        pytest.param(
            EmailEvent(
                event=EventEmail.BOUNCE,
                email="bad@example.com",
                message_id="MSG456",
                event_id="EVT456",
                on_datetime=datetime(2025, 12, 16, 10, 40, 0, tzinfo=UTC),
                reason="Invalid recipient",
                response="",
                url="",
                attempt=-1,
            ),
            {
                "event": "bounce",
                "email": "bad@example.com",
                "messageId": "MSG456",
                "eventId": "EVT456",
                "datetime": "2025-12-16T10:40:00+00:00",
                "reason": "Invalid recipient",
                "response": "",
                "url": "",
                "attempt": -1,
            },
            id="bounce_to_dict",
        ),
    ],
)
def test_to_dict(event: EmailEvent, expected: dict) -> None:
    """Test EmailEvent.to_dict converts instance to dictionary."""
    result = event.to_dict()
    assert result == expected
