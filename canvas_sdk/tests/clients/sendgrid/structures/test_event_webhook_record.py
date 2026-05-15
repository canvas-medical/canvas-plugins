from datetime import UTC, datetime

import pytest

from canvas_sdk.clients.sendgrid.structures.event_webhook import EventWebhook
from canvas_sdk.clients.sendgrid.structures.event_webhook_record import EventWebhookRecord
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test EventWebhookRecord dataclass has correct field types."""
    tested = EventWebhookRecord
    fields = {
        "enabled": bool,
        "url": str,
        "group_resubscribe": bool,
        "group_unsubscribe": bool,
        "delivered": bool,
        "spam_report": bool,
        "bounce": bool,
        "unsubscribe": bool,
        "processed": bool,
        "open": bool,
        "click": bool,
        "dropped": bool,
        "friendly_name": str,
        "id": str,
        "public_key": str,
        "created_date": datetime,
        "updated_date": datetime,
    }
    assert is_dataclass(tested, fields)
    assert issubclass(tested, EventWebhook)


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param(
            {
                "enabled": True,
                "url": "https://example.com/webhook",
                "group_resubscribe": False,
                "group_unsubscribe": True,
                "delivered": True,
                "spam_report": True,
                "bounce": True,
                "unsubscribe": True,
                "processed": False,
                "open": True,
                "click": True,
                "dropped": True,
                "friendly_name": "My Webhook",
                "id": "WEBHOOK123",
                "public_key": "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE",
                "created_date": "2025-12-15T10:30:00Z",
                "updated_date": "2025-12-16T14:20:00Z",
            },
            EventWebhookRecord(
                enabled=True,
                url="https://example.com/webhook",
                group_resubscribe=False,
                group_unsubscribe=True,
                delivered=True,
                spam_report=True,
                bounce=True,
                unsubscribe=True,
                processed=False,
                open=True,
                click=True,
                dropped=True,
                friendly_name="My Webhook",
                id="WEBHOOK123",
                public_key="MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE",
                created_date=datetime(2025, 12, 15, 10, 30, 0, tzinfo=UTC),
                updated_date=datetime(2025, 12, 16, 14, 20, 0, tzinfo=UTC),
            ),
            id="full_webhook_record",
        ),
        pytest.param(
            {
                "enabled": False,
                "url": "https://test.com/hook",
                "group_resubscribe": 0,
                "group_unsubscribe": 0,
                "delivered": 1,
                "spam_report": 0,
                "bounce": 1,
                "unsubscribe": 0,
                "processed": 1,
                "open": 0,
                "click": 0,
                "dropped": 0,
                "friendly_name": "Test Webhook",
                "id": "WEBHOOK456",
                "created_date": "2025-12-17T09:15:00Z",
                "updated_date": "2025-12-17T09:15:00Z",
            },
            EventWebhookRecord(
                enabled=False,
                url="https://test.com/hook",
                group_resubscribe=False,
                group_unsubscribe=False,
                delivered=True,
                spam_report=False,
                bounce=True,
                unsubscribe=False,
                processed=True,
                open=False,
                click=False,
                dropped=False,
                friendly_name="Test Webhook",
                id="WEBHOOK456",
                public_key="",
                created_date=datetime(2025, 12, 17, 9, 15, 0, tzinfo=UTC),
                updated_date=datetime(2025, 12, 17, 9, 15, 0, tzinfo=UTC),
            ),
            id="webhook_record_no_public_key",
        ),
    ],
)
def test_from_dict(data: dict, expected: EventWebhookRecord) -> None:
    """Test EventWebhookRecord.from_dict creates instance from dictionary."""
    test = EventWebhookRecord
    result = test.from_dict(data)
    assert result == expected


@pytest.mark.parametrize(
    ("webhook_record", "expected"),
    [
        pytest.param(
            EventWebhookRecord(
                enabled=True,
                url="https://example.com/webhook",
                group_resubscribe=False,
                group_unsubscribe=True,
                delivered=True,
                spam_report=True,
                bounce=True,
                unsubscribe=True,
                processed=False,
                open=True,
                click=True,
                dropped=True,
                friendly_name="My Webhook",
                id="WEBHOOK123",
                public_key="MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE",
                created_date=datetime(2025, 12, 15, 10, 30, 0, tzinfo=UTC),
                updated_date=datetime(2025, 12, 16, 14, 20, 0, tzinfo=UTC),
            ),
            {
                "enabled": True,
                "url": "https://example.com/webhook",
                "group_resubscribe": False,
                "group_unsubscribe": True,
                "delivered": True,
                "spam_report": True,
                "bounce": True,
                "unsubscribe": True,
                "processed": False,
                "open": True,
                "click": True,
                "dropped": True,
                "friendly_name": "My Webhook",
                "id": "WEBHOOK123",
                "public_key": "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE",
                "created_date": "2025-12-15T10:30:00Z",
                "updated_date": "2025-12-15T10:30:00Z",
            },
            id="webhook_record_to_dict",
        ),
    ],
)
def test_to_dict(webhook_record: EventWebhookRecord, expected: dict) -> None:
    """Test EventWebhookRecord.to_dict converts instance to dictionary."""
    result = webhook_record.to_dict()
    assert result == expected
