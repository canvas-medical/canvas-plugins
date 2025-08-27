import datetime
import json
from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from pydantic_core import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.note.appointment import ScheduleEvent
from canvas_sdk.v1.data.note import NoteTypeCategories


@pytest.fixture
def mock_db_queries() -> Generator[dict[str, MagicMock]]:
    """Mock all database queries to return True/exist by default."""
    with (
        patch("canvas_sdk.v1.data.PracticeLocation.objects") as mock_pl,
        patch("canvas_sdk.v1.data.Staff.objects") as mock_staff,
        patch("canvas_sdk.v1.data.Patient.objects") as mock_patient,
        patch("canvas_sdk.v1.data.NoteType.objects") as mock_note_type,
        patch("canvas_sdk.v1.data.appointment.Appointment.objects") as mock_appointment,
    ):
        # Setup default behaviors
        mock_pl.filter.return_value.exists.return_value = True
        mock_staff.filter.return_value.exists.return_value = True
        mock_patient.filter.return_value.exists.return_value = True
        mock_appointment.filter.return_value.exists.return_value = True

        # Note type default behavior for schedule events
        mock_note_type.values.return_value.filter.return_value.first.return_value = {
            "category": NoteTypeCategories.SCHEDULE_EVENT,
            "is_patient_required": False,
            "allow_custom_title": True,
        }

        yield {
            "practice_location": mock_pl,
            "staff": mock_staff,
            "patient": mock_patient,
            "note_type": mock_note_type,
            "appointment": mock_appointment,
        }


@pytest.fixture
def valid_schedule_event_data() -> dict[str, Any]:
    """Valid data for creating a ScheduleEvent."""
    return {
        "practice_location_id": str(uuid4()),
        "provider_id": str(uuid4()),
        "note_type_id": str(uuid4()),
        "start_time": datetime.datetime.now(),
        "duration_minutes": 60,
        "description": "Team Meeting",
    }


def test_create_schedule_event_success(
    mock_db_queries: dict[str, MagicMock], valid_schedule_event_data: dict[str, Any]
) -> None:
    """Test successful schedule event creation."""
    event = ScheduleEvent(**valid_schedule_event_data)
    effect = event.create()

    assert effect.type == EffectType.CREATE_SCHEDULE_EVENT
    payload = json.loads(effect.payload)
    assert payload["data"]["note_type_id"] == valid_schedule_event_data["note_type_id"]
    assert payload["data"]["description"] == "Team Meeting"
    assert payload["data"]["start_time"] is not None
    assert payload["data"]["duration_minutes"] == 60


def test_create_schedule_event_missing_note_type(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test schedule event creation without note_type_id."""
    event = ScheduleEvent(
        practice_location_id=str(uuid4()),
        provider_id=str(uuid4()),
        start_time=datetime.datetime.now(),
        duration_minutes=60,
    )

    with pytest.raises(ValidationError) as exc_info:
        event.create()

    errors = exc_info.value.errors()
    error_fields = [e["msg"] for e in errors]
    assert "Field 'note_type_id' is required to create a schedule event." in error_fields


def test_create_schedule_event_missing_base_fields(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test schedule event creation missing base class required fields."""
    event = ScheduleEvent(
        note_type_id=str(uuid4()), start_time=datetime.datetime.now(), duration_minutes=60
    )

    with pytest.raises(ValidationError) as exc_info:
        event.create()

    errors = exc_info.value.errors()
    error_fields = [e["msg"] for e in errors]
    assert "Practice location ID is required." in error_fields
    assert "Provider ID is required." in error_fields


def test_create_schedule_event_missing_appointment_fields(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test schedule event creation missing appointment-specific required fields."""
    event = ScheduleEvent(
        practice_location_id=str(uuid4()), provider_id=str(uuid4()), note_type_id=str(uuid4())
    )

    with pytest.raises(ValidationError) as exc_info:
        event.create()

    errors = exc_info.value.errors()
    error_fields = [e["msg"] for e in errors]
    assert "Field 'start_time' is required to create an appointment." in error_fields
    assert "Field 'duration_minutes' is required to create an appointment." in error_fields


def test_schedule_event_with_patient(
    mock_db_queries: dict[str, MagicMock], valid_schedule_event_data: dict[str, Any]
) -> None:
    """Test schedule event with optional patient."""
    valid_schedule_event_data["patient_id"] = str(uuid4())

    event = ScheduleEvent(**valid_schedule_event_data)
    effect = event.create()

    payload = json.loads(effect.payload)
    assert payload["data"]["patient_id"] == valid_schedule_event_data["patient_id"]


def test_schedule_event_patient_required(
    mock_db_queries: dict[str, MagicMock], valid_schedule_event_data: dict[str, Any]
) -> None:
    """Test schedule event when patient is required by note type."""
    mock_note_type = mock_db_queries["note_type"]
    mock_note_type.values.return_value.filter.return_value.first.return_value = {
        "category": NoteTypeCategories.SCHEDULE_EVENT,
        "is_patient_required": True,
        "allow_custom_title": True,
    }

    # No patient_id provided
    event = ScheduleEvent(**valid_schedule_event_data)

    with pytest.raises(ValidationError) as exc_info:
        event.create()

    errors = exc_info.value.errors()
    assert any("Patient ID is required for this note type" in str(e) for e in errors)


def test_schedule_event_no_custom_title_allowed(
    mock_db_queries: dict[str, MagicMock], valid_schedule_event_data: dict[str, Any]
) -> None:
    """Test schedule event when custom title is not allowed."""
    mock_note_type = mock_db_queries["note_type"]
    mock_note_type.values.return_value.filter.return_value.first.return_value = {
        "category": NoteTypeCategories.SCHEDULE_EVENT,
        "is_patient_required": False,
        "allow_custom_title": False,
    }

    event = ScheduleEvent(**valid_schedule_event_data)

    with pytest.raises(ValidationError) as exc_info:
        event.create()

    errors = exc_info.value.errors()
    assert any("Description is not allowed for this note type" in str(e) for e in errors)


def test_schedule_event_invalid_note_type_category(
    mock_db_queries: dict[str, MagicMock], valid_schedule_event_data: dict[str, Any]
) -> None:
    """Test schedule event with wrong note type category."""
    mock_note_type = mock_db_queries["note_type"]
    mock_note_type.values.return_value.filter.return_value.first.return_value = {
        "category": NoteTypeCategories.ENCOUNTER,  # Wrong category
        "is_patient_required": False,
        "allow_custom_title": True,
    }

    event = ScheduleEvent(**valid_schedule_event_data)

    with pytest.raises(ValidationError) as exc_info:
        event.create()

    errors = exc_info.value.errors()
    assert any("Schedule event note type must be of type: schedule_event" in str(e) for e in errors)


def test_schedule_event_note_type_not_found(
    mock_db_queries: dict[str, MagicMock], valid_schedule_event_data: dict[str, Any]
) -> None:
    """Test when note type doesn't exist."""
    mock_note_type = mock_db_queries["note_type"]
    mock_note_type.values.return_value.filter.return_value.first.return_value = None

    event = ScheduleEvent(**valid_schedule_event_data)

    with pytest.raises(ValidationError) as exc_info:
        event.create()

    errors = exc_info.value.errors()
    assert any("Note type with ID" in str(e) and "does not exist" in str(e) for e in errors)


def test_schedule_event_update_success(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test schedule event update."""
    event = ScheduleEvent(instance_id=str(uuid4()))
    event.start_time = datetime.datetime.now()
    event.description = "Updated Meeting"
    event.duration_minutes = 90

    effect = event.update()

    assert effect.type == EffectType.UPDATE_SCHEDULE_EVENT
    payload = json.loads(effect.payload)
    assert "start_time" in payload["data"]
    assert payload["data"]["description"] == "Updated Meeting"
    assert payload["data"]["duration_minutes"] == 90


def test_schedule_event_update_no_changes_fails(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that update with no changes raises error."""
    event = ScheduleEvent(instance_id=str(uuid4()))

    with pytest.raises(ValueError) as exc_info:
        event.update()

    assert "No fields have been modified" in str(exc_info.value)


def test_schedule_event_partial_update(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test updating only one field."""
    event = ScheduleEvent(instance_id=str(uuid4()))
    event.description = "Only Description Updated"

    effect = event.update()
    payload = json.loads(effect.payload)

    # Should only contain instance_id and description
    assert set(payload["data"].keys()) == {"instance_id", "description"}
    assert payload["data"]["description"] == "Only Description Updated"


def test_schedule_event_delete(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test schedule event deletion."""
    event = ScheduleEvent(instance_id=str(uuid4()))
    event.description = "To be deleted"

    effect = event.delete()

    assert effect.type == EffectType.DELETE_SCHEDULE_EVENT
    payload = json.loads(effect.payload)
    # Delete sends all dirty fields (current implementation)
    assert payload["data"]["description"] == "To be deleted"
    assert "instance_id" in payload["data"]


def test_schedule_event_delete_missing_instance_id(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that delete without instance_id raises error."""
    event = ScheduleEvent(practice_location_id=str(uuid4()), provider_id=str(uuid4()))

    with pytest.raises(ValidationError) as exc_info:
        event.delete()

    errors = exc_info.value.errors()
    assert any("instance_id' is required" in str(e) for e in errors)


def test_schedule_event_nonexistent_references(
    mock_db_queries: dict[str, MagicMock], valid_schedule_event_data: dict[str, Any]
) -> None:
    """Test validation when referenced entities don't exist."""
    mock_db_queries["patient"].filter.return_value.exists.return_value = False
    mock_db_queries["practice_location"].filter.return_value.exists.return_value = False

    # Add patient_id to test patient validation
    valid_schedule_event_data["patient_id"] = str(uuid4())

    event = ScheduleEvent(**valid_schedule_event_data)

    with pytest.raises(ValidationError) as exc_info:
        event.create()

    errors = exc_info.value.errors()
    error_messages = [str(e) for e in errors]
    assert any("Practice location with ID" in msg for msg in error_messages)
    assert any("Patient with ID" in msg for msg in error_messages)


def test_schedule_event_update_nonexistent_schedule_event(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test updating a schedule event that doesn't exist."""
    mock_db_queries["appointment"].filter.return_value.exists.return_value = False

    event = ScheduleEvent(instance_id=str(uuid4()))
    event.description = "Updated"

    with pytest.raises(ValidationError) as exc_info:
        event.update()

    errors = exc_info.value.errors()
    assert any("Appointment with ID" in str(e) and "does not exist" in str(e) for e in errors)


def test_schedule_event_with_all_fields(
    mock_db_queries: dict[str, MagicMock], valid_schedule_event_data: dict[str, Any]
) -> None:
    """Test creating a schedule event with all possible fields."""
    valid_schedule_event_data["patient_id"] = str(uuid4())

    event = ScheduleEvent(**valid_schedule_event_data)
    effect = event.create()

    payload = json.loads(effect.payload)
    expected_fields = {
        "practice_location_id",
        "provider_id",
        "note_type_id",
        "start_time",
        "duration_minutes",
        "description",
        "patient_id",
    }
    assert set(payload["data"].keys()) == expected_fields


def test_schedule_event_without_optional_fields(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test creating a schedule event without optional fields."""
    event = ScheduleEvent(
        practice_location_id=str(uuid4()),
        provider_id=str(uuid4()),
        note_type_id=str(uuid4()),
        start_time=datetime.datetime.now(),
        duration_minutes=60,
        # No description or patient_id
    )

    effect = event.create()
    payload = json.loads(effect.payload)

    assert "description" not in payload["data"]
    assert "patient_id" not in payload["data"]
    assert effect.type == EffectType.CREATE_SCHEDULE_EVENT


def test_create_schedule_event_parent_appointment_equals_instance_id(
    mock_db_queries: dict[str, MagicMock], valid_schedule_event_data: dict[str, Any]
) -> None:
    """Test that parent appointment cannot be the same as instance_id on creation."""
    same_id = str(uuid4())
    schedule_event_data = {
        **valid_schedule_event_data,
        "instance_id": same_id,
        "parent_appointment_id": same_id,
    }
    event = ScheduleEvent(**schedule_event_data)

    with pytest.raises(ValidationError) as exc_info:
        event.create()

    errors = exc_info.value.errors()
    assert any("parent_appointment_id cannot be the same as instance_id" in str(e) for e in errors)


def test_update_schedule_event_appointment_equals_instance_id(
    mock_db_queries: dict[str, MagicMock], valid_schedule_event_data: dict[str, Any]
) -> None:
    """Test that parent appointment cannot be the same as instance_id on update."""
    same_id = str(uuid4())
    schedule_event_data = {
        **valid_schedule_event_data,
        "instance_id": same_id,
        "parent_appointment_id": same_id,
    }
    event = ScheduleEvent(**schedule_event_data)

    with pytest.raises(ValidationError) as exc_info:
        event.update()

    errors = exc_info.value.errors()
    assert any(
        "parent_appointment_id can only be set when creating an appointment." in str(e)
        for e in errors
    )
