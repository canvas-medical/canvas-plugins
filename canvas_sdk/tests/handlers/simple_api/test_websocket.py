import json
from collections.abc import Mapping

import pytest

from canvas_sdk.effects.simple_api import AcceptConnection, DenyConnection
from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.handlers.simple_api.tools import CaseInsensitiveMultiDict, separate_headers
from canvas_sdk.handlers.simple_api.websocket import WebSocketAPI
from canvas_sdk.tests.shared import params_from_dict


def make_auth_event(
    channel: str,
    headers: Mapping[str, str] | None = None,
) -> Event:
    """Make a SIMPLE_API_WEBSOCKET_AUTHENTICATE event suitable for testing."""
    return Event(
        event_request=EventRequest(
            type=EventType.SIMPLE_API_WEBSOCKET_AUTHENTICATE,
            target=None,
            context=json.dumps(
                {
                    "channel_name": channel,
                    "headers": dict(headers) if headers else {},
                },
                indent=None,
                separators=(",", ":"),
            ),
            target_type=None,
        )
    )


USER = {
    "canvas-logged-in-user-id": "id",
    "canvas-logged-in-user-type": "Staff",
}

HEADERS = CaseInsensitiveMultiDict(
    separate_headers(
        {
            **USER,
            "authorization": "key",
        }
    )
)


@pytest.mark.parametrize(
    ("property", "expected_value"),
    params_from_dict(
        {
            "channel": ("channel", "test_channel"),
            "headers": ("headers", HEADERS),
            "logged_in_user": (
                "logged_in_user",
                {
                    "id": USER["canvas-logged-in-user-id"],
                    "type": USER["canvas-logged-in-user-type"],
                },
            ),
            "key": ("key", HEADERS.get("authorization")),
        }
    ),
)
def test_websocket_properties(property: str, expected_value: str) -> None:
    """Test the properties of the WebSocket class."""
    event = make_auth_event(
        channel="test_channel",
        headers=HEADERS,
    )

    handler = WebSocketAPI(event=event)

    assert getattr(handler.websocket, property) == expected_value


def test_session_based_authentication() -> None:
    """Test the session-based authentication."""
    event = make_auth_event(
        channel="test_channel",
        headers=HEADERS,
    )

    class SessionAuthWebSocketAPI(WebSocketAPI):
        def authenticate(self) -> bool:
            return (
                self.websocket.logged_in_user is not None
                and self.websocket.logged_in_user.get("id") == USER["canvas-logged-in-user-id"]
                and self.websocket.logged_in_user.get("type") == USER["canvas-logged-in-user-type"]
            )

    handler = SessionAuthWebSocketAPI(event=event)

    assert handler.compute() == [AcceptConnection().apply()]


def test_key_based_authentication() -> None:
    """Test the key-based authentication."""
    event = make_auth_event(
        channel="test_channel",
        headers=HEADERS,
    )

    class KeyAuthWebSocketAPI(WebSocketAPI):
        def authenticate(self) -> bool:
            return self.websocket.key == self.secrets.get("key")

    handler = KeyAuthWebSocketAPI(event=event, secrets={"key": HEADERS.get("authorization")})

    assert handler.compute() == [AcceptConnection().apply()]


def test_unauthorized_request() -> None:
    """Test an unauthorized request."""
    event = make_auth_event(
        channel="test_channel",
        headers=HEADERS,
    )

    class InvalidAuthentication(WebSocketAPI):
        def authenticate(self) -> bool:
            return False

    handler = InvalidAuthentication(event=event)

    assert handler.compute() == [DenyConnection(message="Unauthorized").apply()]
