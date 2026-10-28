import json
from collections.abc import Mapping

import pytest

from canvas_sdk.effects.simple_api import AcceptConnection, DenyConnection
from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.handlers.simple_api.security import PortalAccessLevel
from canvas_sdk.handlers.simple_api.tools import CaseInsensitiveMultiDict, separate_headers
from canvas_sdk.handlers.simple_api.websocket import WebSocketAPI
from canvas_sdk.tests.shared import params_from_dict
from plugin_runner.exceptions import PluginError


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
            "api_key": ("api_key", HEADERS.get("authorization")),
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
            return self.websocket.api_key == self.secrets.get("key")

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


PATIENT = {
    "canvas-logged-in-user-id": "patient-key",
    "canvas-logged-in-user-type": "Patient",
}


def acting(**levels: str) -> dict[str, str]:
    """Headers for another login acting on the patient's chart, with its access by area."""
    return {
        **PATIENT,
        "canvas-logged-in-acting-user-id": "42",
        **{f"canvas-logged-in-access-{area}": level for area, level in levels.items()},
    }


def test_portal_access() -> None:
    """A login acting on a patient's chart is named, with the access it was given."""
    event = make_auth_event(channel="test_channel", headers=acting(messaging="view"))

    portal_access = WebSocketAPI(event=event).websocket.portal_access

    assert portal_access.acting_user_id == "42"
    assert portal_access.level("messaging") == PortalAccessLevel.VIEW
    assert portal_access.level("billing") == PortalAccessLevel.NONE


class PatientWebSocketAPI(WebSocketAPI):
    """Accepts any patient session, and nothing else."""

    def authenticate(self) -> bool:
        """Accept a patient session."""
        return (
            self.websocket.logged_in_user is not None
            and self.websocket.logged_in_user["type"] == "Patient"
        )


class MessagingWebSocketAPI(PatientWebSocketAPI):
    """Also admits a login acting on a patient's chart that may view messages."""

    PORTAL_ACCESS = {"messaging": PortalAccessLevel.VIEW}


ACCEPTED = [AcceptConnection().apply()]
DENIED = [DenyConnection(message="Unauthorized").apply()]


@pytest.mark.parametrize(
    ("handler_class", "headers", "expected_effects"),
    [
        (PatientWebSocketAPI, PATIENT, ACCEPTED),
        (PatientWebSocketAPI, acting(messaging="act"), DENIED),
        (MessagingWebSocketAPI, PATIENT, ACCEPTED),
        (MessagingWebSocketAPI, acting(messaging="view"), ACCEPTED),
        (MessagingWebSocketAPI, acting(messaging="none"), DENIED),
        (MessagingWebSocketAPI, acting(), DENIED),
    ],
    ids=[
        "own chart, no declaration",
        "acting, no declaration",
        "own chart, declared",
        "acting with view, declared",
        "acting with none, declared",
        "acting with no level, declared",
    ],
)
def test_portal_access_is_enforced(
    handler_class: type[WebSocketAPI], headers: Mapping[str, str], expected_effects: list
) -> None:
    """A login acting on a patient's chart connects only with the access PORTAL_ACCESS requires."""
    event = make_auth_event(channel="test_channel", headers=headers)

    assert handler_class(event=event).compute() == expected_effects


def test_portal_access_without_a_session() -> None:
    """A connection without a patient session has no portal access."""

    class MessagingOnly(WebSocketAPI):
        def authenticate(self) -> bool:
            return self.websocket.portal_access.allows("messaging", PortalAccessLevel.VIEW)

    event = make_auth_event(channel="test_channel")

    assert MessagingOnly(event=event).compute() == DENIED


def test_portal_access_declaration_is_checked() -> None:
    """A PORTAL_ACCESS the SDK can't enforce is an error when the plugin loads."""
    with pytest.raises(PluginError, match="Unknown portal area 'pharmacy'"):

        class Pharmacy(WebSocketAPI):
            PORTAL_ACCESS = {"pharmacy": "view"}
