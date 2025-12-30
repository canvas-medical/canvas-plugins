import pytest

from canvas_sdk.clients.sendgrid.structures.event_webhook import EventWebhook
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test EventWebhook dataclass has correct field types."""
    tested = EventWebhook
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
    }
    assert is_dataclass(tested, fields)


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
            },
            EventWebhook(
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
            ),
            id="full_webhook",
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
            },
            EventWebhook(
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
            ),
            id="webhook_with_integers",
        ),
    ],
)
def test_from_dict(data: dict, expected: EventWebhook) -> None:
    """Test EventWebhook.from_dict creates instance from dictionary."""
    test = EventWebhook
    result = test.from_dict(data)
    assert result == expected


@pytest.mark.parametrize(
    ("webhook", "expected"),
    [
        pytest.param(
            EventWebhook(
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
            },
            id="webhook_to_dict",
        ),
    ],
)
def test_to_dict(webhook: EventWebhook, expected: dict) -> None:
    """Test EventWebhook.to_dict converts instance to dictionary."""
    result = webhook.to_dict()
    assert result == expected
