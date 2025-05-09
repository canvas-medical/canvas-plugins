import json
from collections.abc import Mapping

import pytest

from canvas_sdk.effects.simple_api import AcceptConnection, DenyConnection
from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.handlers.simple_api import WebSocketAPI


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

HEADERS = {
    **USER,
    "authorization": "test_token",
}


@pytest.mark.parametrize(
    argnames="property,expected_value",
    argvalues=[
        ("channel", "test_channel"),
        ("headers", HEADERS),
        (
            "logged_in_user",
            {"id": USER["canvas-logged-in-user-id"], "type": USER["canvas-logged-in-user-type"]},
        ),
        ("auth_token", HEADERS.get("authorization")),
    ],
    ids=["channel", "headers", "logged_in_user", "auth_token"],
)
def test_properties(property: str, expected_value: str) -> None:
    """Test the properties of the WebSocketAPI class."""
    event = make_auth_event(
        channel="test_channel",
        headers=HEADERS,
    )

    handler = WebSocketAPI(event=event)

    # Check if the property returns the expected value
    assert getattr(handler, property) == expected_value


def test_session_based_authentication() -> None:
    """Test the session-based authentication."""
    event = make_auth_event(
        channel="test_channel",
        headers=HEADERS,
    )

    class SessionAuthWebSocketAPI(WebSocketAPI):
        def authenticate(self) -> bool:
            return (
                self.logged_in_user is not None
                and self.logged_in_user.get("id") == USER["canvas-logged-in-user-id"]
                and self.logged_in_user.get("type") == USER["canvas-logged-in-user-type"]
            )

    handler = SessionAuthWebSocketAPI(event=event)

    assert handler.compute() == [AcceptConnection().apply()]


def test_token_based_authentication() -> None:
    """Test the token-based authentication."""
    event = make_auth_event(
        channel="test_channel",
        headers=HEADERS,
    )

    class SessionWebSocketAPI(WebSocketAPI):
        def authenticate(self) -> bool:
            return self.auth_token == self.secrets.get("token")

    handler = SessionWebSocketAPI(event=event, secrets={"token": HEADERS.get("authorization")})

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
