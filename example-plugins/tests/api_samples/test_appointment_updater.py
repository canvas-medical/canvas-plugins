from http import HTTPStatus

import pytest
from api_samples.routes.appointment_updater import AppointmentAPI

from canvas_sdk.test_utils.factories import NoteFactory
from tests.factories import AppointmentFactory


class DummyRequest:
    """A dummy request object for testing AppointmentAPI."""

    def __init__(self, path_params=None, json_body=None):
        self.path_params = path_params or {}
        self._json_body = json_body or {}

    def json(self):
        """Return the mocked JSON body."""
        return self._json_body


class DummyEvent:
    """A dummy event object for testing API handlers."""

    def __init__(self, context=None):
        self.context = context or {}


@pytest.mark.django_db
def test_appointment_api_put():
    """Test the put method of AppointmentAPI for updating an appointment.

    This test uses real database objects via factories to test the API in a more
    realistic scenario compared to using mocks.
    """
    # Create a real note (which creates patient, provider, location automatically)
    note = NoteFactory.create()

    # Create a real appointment associated with the note
    appointment = AppointmentFactory.create(
        note=note,
        patient=note.patient,
        provider=note.provider,
        location=note.location,
        status="confirmed",
    )

    # Verify appointment was created
    assert appointment.id is not None
    assert appointment.note == note

    # Create the API request
    request = DummyRequest(
        path_params={"id": str(note.dbid)},  # Use note's dbid for lookup
        json_body={"meetingLink": "https://meet.example.com/test-meeting"},
    )

    # Create API instance
    dummy_context = {"method": "PUT", "path": f"/appointments/{note.dbid}"}
    api = AppointmentAPI(event=DummyEvent(context=dummy_context))
    api.request = request

    # Execute the API call
    result = api.put()

    # Verify results - API returns an effect and a response
    assert len(result) == 2
    assert any(getattr(r, "status_code", None) == HTTPStatus.ACCEPTED for r in result)

    # Verify the effect was created correctly
    # Note: Effects need to be applied separately to actually update the database
    # This test verifies the API correctly creates the effect
    effect = [r for r in result if hasattr(r, "apply")][0]
    assert effect is not None


@pytest.mark.django_db
def test_appointment_api_put_not_found():
    """Test the put method returns 404 when appointment doesn't exist."""
    # Create API request for non-existent appointment
    request = DummyRequest(
        path_params={"id": "99999"},  # Non-existent note ID
        json_body={"meetingLink": "https://meet.example.com/test"},
    )

    # Create API instance with proper context
    dummy_context = {"method": "PUT", "path": "/appointments/99999"}
    api = AppointmentAPI(event=DummyEvent(context=dummy_context))
    api.request = request

    # Execute the API call
    result = api.put()

    # Verify 404 response
    assert len(result) == 1
    assert result[0].status_code == HTTPStatus.NOT_FOUND

