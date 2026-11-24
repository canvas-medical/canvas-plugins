"""Tests for who the SendGrid email routes admit, and the hand-off between the two handlers."""

import json
from base64 import b64encode
from http import HTTPStatus
from typing import Any
from unittest.mock import patch

import pytest
from sendgrid_email.handlers.email_manip import EmailManip, SendGridCallbacks

from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.handlers.simple_api import SimpleAPI

STAFF = {"canvas-logged-in-user-type": "Staff", "canvas-logged-in-user-id": "a" * 32}
PATIENT = {"canvas-logged-in-user-type": "Patient", "canvas-logged-in-user-id": "b" * 32}

DELIVERED = {
    "event": "delivered",
    "email": "someone@example.com",
    "sg_message_id": "message-1",
    "sg_event_id": "event-1",
    "timestamp": 1_700_000_000,
    "response": "250 OK",
}


class FakeCache:
    """An in-memory stand-in for the plugin cache."""

    def __init__(self) -> None:
        self.values: dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        """Store a value."""
        self.values[key] = value

    def get(self, key: str) -> Any:
        """Return a stored value, or None."""
        return self.values.get(key)


def event(
    event_type: EventType, method: str, path: str, headers: dict[str, str], body: bytes = b""
) -> Event:
    """Build a SimpleAPI event for one request."""
    return Event(
        EventRequest(
            type=event_type,
            context=json.dumps(
                {
                    "method": method,
                    "path": path,
                    "query_string": "",
                    "body": b64encode(body).decode(),
                    "headers": headers,
                }
            ),
        )
    )


def authenticate(
    handler: type[SimpleAPI], method: str, path: str, headers: dict[str, str]
) -> HTTPStatus:
    """Send the authenticate event for one request and return the status it answers."""
    effects = handler(event(EventType.SIMPLE_API_AUTHENTICATE, method, path, headers)).compute()
    return HTTPStatus(json.loads(effects[0].payload)["status_code"])


@pytest.mark.parametrize(
    ("headers", "expected"),
    [
        ({}, HTTPStatus.UNAUTHORIZED),
        (PATIENT, HTTPStatus.UNAUTHORIZED),
        (STAFF, HTTPStatus.OK),
    ],
    ids=["no_session", "patient_session", "staff_session"],
)
def test_reading_stored_email_needs_a_staff_session(
    headers: dict[str, str], expected: HTTPStatus
) -> None:
    """The routes that send email or read what SendGrid stored answer only to signed-in staff."""
    assert authenticate(EmailManip, "GET", "/outbound_email_status", headers) == expected


def test_sendgrid_callbacks_are_admitted_without_a_session() -> None:
    """SendGrid's own posts carry no Canvas session and are still accepted."""
    assert authenticate(SendGridCallbacks, "POST", "/outbound_email_status", {}) == HTTPStatus.OK


def test_a_status_sendgrid_posts_is_read_back_by_staff() -> None:
    """A status event stored by the callback route comes back from the staff route."""
    cache = FakeCache()
    body = json.dumps([DELIVERED]).encode()
    post = event(EventType.SIMPLE_API_REQUEST, "POST", "/outbound_email_status", {}, body)
    get = event(EventType.SIMPLE_API_REQUEST, "GET", "/outbound_email_status", STAFF)

    with patch("sendgrid_email.handlers.email_manip.get_cache", return_value=cache):
        saved = SendGridCallbacks(post).outbound_status_save()
        read = EmailManip(get).last_outbound_status()

    assert saved[0].status_code == HTTPStatus.OK
    assert [(e["event"], e["messageId"]) for e in json.loads(read[0].content)] == [
        ("delivered", "message-1")
    ]
