"""Tests for who the LLM API admits."""

import json
from base64 import b64encode
from http import HTTPStatus

import pytest
from llm_manip.handlers.llm_manip import LlmManip

from canvas_sdk.events import Event, EventRequest, EventType

STAFF = {"canvas-logged-in-user-type": "Staff", "canvas-logged-in-user-id": "a" * 32}
PATIENT = {"canvas-logged-in-user-type": "Patient", "canvas-logged-in-user-id": "b" * 32}


def authenticate(headers: dict[str, str]) -> HTTPStatus:
    """Send the authenticate event for POST /chat/0 and return the status it answers."""
    event = Event(
        EventRequest(
            type=EventType.SIMPLE_API_AUTHENTICATE,
            context=json.dumps(
                {
                    "method": "POST",
                    "path": "/chat/0",
                    "query_string": "",
                    "body": b64encode(b"").decode(),
                    "headers": headers,
                }
            ),
        )
    )
    effects = LlmManip(event).compute()
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
def test_only_a_staff_session_is_admitted(headers: dict[str, str], expected: HTTPStatus) -> None:
    """The routes that spend the practice's LLM keys answer only to signed-in staff."""
    assert authenticate(headers) == expected
