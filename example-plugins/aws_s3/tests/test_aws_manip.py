"""Tests for who the S3 API admits."""

import json
from base64 import b64encode
from http import HTTPStatus

import pytest
from aws_manip.handlers.aws_manip import AwsManip

from canvas_sdk.events import Event, EventRequest, EventType

STAFF = {"canvas-logged-in-user-type": "Staff", "canvas-logged-in-user-id": "a" * 32}
PATIENT = {"canvas-logged-in-user-type": "Patient", "canvas-logged-in-user-id": "b" * 32}


def authenticate(headers: dict[str, str]) -> HTTPStatus:
    """Send the authenticate event for GET /list_items and return the status it answers."""
    event = Event(
        EventRequest(
            type=EventType.SIMPLE_API_AUTHENTICATE,
            context=json.dumps(
                {
                    "method": "GET",
                    "path": "/list_items",
                    "query_string": "",
                    "body": b64encode(b"").decode(),
                    "headers": headers,
                }
            ),
        )
    )
    effects = AwsManip(event).compute()
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
    """The S3 routes answer only to signed-in staff."""
    assert authenticate(headers) == expected
