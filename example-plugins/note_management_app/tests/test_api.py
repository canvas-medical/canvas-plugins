"""Tests for who the note management app's page and note routes admit."""

import json
from base64 import b64encode
from http import HTTPStatus

import pytest
from note_management_app.handlers.api import AppApi, NoteApi

from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.handlers.simple_api import SimpleAPI
from canvas_sdk.test_utils.factories import CanvasUserFactory


def authenticate(handler: type[SimpleAPI], path: str, actor: str = "") -> HTTPStatus:
    """Send the authenticate event for GET <path> and return the status it answers."""
    event = Event(
        EventRequest(
            type=EventType.SIMPLE_API_AUTHENTICATE,
            actor=actor,
            context=json.dumps(
                {
                    "method": "GET",
                    "path": path,
                    "query_string": "",
                    "body": b64encode(b"").decode(),
                    "headers": {},
                }
            ),
        )
    )
    effects = handler(event).compute()
    return HTTPStatus(json.loads(effects[0].payload)["status_code"])


def test_the_page_is_served_without_a_session() -> None:
    """The page holds no data, so anyone may load it and sign in through OAuth."""
    assert authenticate(AppApi, "/app") == HTTPStatus.OK


@pytest.mark.django_db
def test_the_recent_notes_route_needs_a_canvas_user() -> None:
    """Listing notes is refused unless the request comes from a Canvas user."""
    user = CanvasUserFactory.create()

    assert authenticate(NoteApi, "/notes/recent") == HTTPStatus.UNAUTHORIZED
    assert authenticate(NoteApi, "/notes/recent", actor=str(user.dbid)) == HTTPStatus.OK
