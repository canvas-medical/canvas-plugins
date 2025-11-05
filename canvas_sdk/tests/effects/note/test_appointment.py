import datetime
import json
from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from pydantic_core import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.note import AppointmentIdentifier
from canvas_sdk.effects.note.appointment import Appointment
from canvas_sdk.v1.data.appointment import AppointmentProgressStatus
from canvas_sdk.v1.data.note import NoteType, NoteTypeCategories


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

        # Note type default behavior
        mock_note_type.values_list.return_value.get.return_value = (
            NoteTypeCategories.ENCOUNTER,
            True,  # category, is_scheduleable
        )

        yield {
            "practice_location": mock_pl,
            "staff": mock_staff,
            "patient": mock_patient,
            "note_type": mock_note_type,
            "appointment": mock_appointment,
        }


@pytest.fixture
def valid_appointment_data() -> dict[str, Any]:
    """Valid data for creating an Appointment."""
    return {
        "practice_location_id": str(uuid4()),
        "provider_id": str(uuid4()),
        "appointment_note_type_id": str(uuid4()),
        "patient_id": str(uuid4()),
        "start_time": datetime.datetime.now(),
        "duration_minutes": 30,
        "meeting_link": "https://example.com/meeting",
        "parent_appointment_id": str(uuid4()),
    }


def test_create_appointment_success(
    mock_db_queries: dict[str, MagicMock], valid_appointment_data: dict[str, Any]
) -> None:
    """Test successful appointment creation."""
    appointment = Appointment(**valid_appointment_data)
    effect = appointment.create()

    assert effect.type == EffectType.CREATE_APPOINTMENT
    payload = json.loads(effect.payload)
    assert (
        payload["data"]["appointment_note_type_id"]
        == valid_appointment_data["appointment_note_type_id"]
    )
    assert payload["data"]["patient_id"] == valid_appointment_data["patient_id"]
    assert payload["data"]["start_time"] is not None
    assert payload["data"]["duration_minutes"] == 30
    assert payload["data"]["meeting_link"] == "https://example.com/meeting"


def test_create_appointment_missing_required_fields(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test appointment creation with missing required fields."""
    appointment = Appointment(
        practice_location_id=str(uuid4()),
        provider_id=str(uuid4()),
        start_time=datetime.datetime.now(),
        duration_minutes=30,
    )

    with pytest.raises(ValidationError) as exc_info:
        appointment.create()

    errors = exc_info.value.errors()
    error_fields = [e["msg"] for e in errors]
    assert "Field 'appointment_note_type_id' is required to create an appointment." in error_fields
    assert "Field 'patient_id' is required to create an appointment." in error_fields


def test_create_appointment_missing_base_fields(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test appointment creation missing base class required fields."""
    appointment = Appointment(
        appointment_note_type_id=str(uuid4()),
        patient_id=str(uuid4()),
        start_time=datetime.datetime.now(),
        duration_minutes=30,
    )

    with pytest.raises(ValidationError) as exc_info:
        appointment.create()

    errors = exc_info.value.errors()
    error_fields = [e["msg"] for e in errors]
    assert "Practice location ID is required." in error_fields
    assert "Provider ID is required." in error_fields


def test_create_appointment_missing_appointment_specific_fields(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test appointment creation missing appointment-specific required fields."""
    appointment = Appointment(
        practice_location_id=str(uuid4()),
        provider_id=str(uuid4()),
        appointment_note_type_id=str(uuid4()),
        patient_id=str(uuid4()),
    )

    with pytest.raises(ValidationError) as exc_info:
        appointment.create()

    errors = exc_info.value.errors()
    error_fields = [e["msg"] for e in errors]
    assert "Field 'start_time' is required to create an appointment." in error_fields
    assert "Field 'duration_minutes' is required to create an appointment." in error_fields


def test_appointment_update_success(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test successful appointment update."""
    appointment = Appointment(instance_id=str(uuid4()))
    appointment.start_time = datetime.datetime.now()
    appointment.meeting_link = "https://new-link.com"
    appointment.status = AppointmentProgressStatus.CONFIRMED

    effect = appointment.update()

    assert effect.type == EffectType.UPDATE_APPOINTMENT
    payload = json.loads(effect.payload)
    assert "start_time" in payload["data"]
    assert payload["data"]["meeting_link"] == "https://new-link.com"
    assert payload["data"]["status"] == AppointmentProgressStatus.CONFIRMED.value


def test_appointment_update_prevents_patient_change(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that updating patient_id raises error."""
    appointment = Appointment(instance_id=str(uuid4()))
    appointment.patient_id = str(uuid4())

    with pytest.raises(ValidationError) as exc_info:
        appointment.update()

    errors = exc_info.value.errors()
    assert any("patient_id' cannot be updated" in str(e) for e in errors)


def test_appointment_update_no_changes_fails(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that update with no changes raises error."""
    appointment = Appointment(instance_id=str(uuid4()))

    with pytest.raises(ValueError) as exc_info:
        appointment.update()

    assert "No fields have been modified" in str(exc_info.value)


def test_appointment_cancel(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test appointment cancellation."""
    appointment = Appointment(instance_id=str(uuid4()))
    appointment.status = AppointmentProgressStatus.CANCELLED

    effect = appointment.cancel()

    assert effect.type == EffectType.CANCEL_APPOINTMENT
    payload = json.loads(effect.payload)
    # Cancel sends all dirty fields
    assert payload["data"]["status"] == AppointmentProgressStatus.CANCELLED.value
    assert "instance_id" in payload["data"]


def test_appointment_cancel_missing_instance_id(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that cancel without instance_id raises error."""
    appointment = Appointment(practice_location_id=str(uuid4()), provider_id=str(uuid4()))

    with pytest.raises(ValidationError) as exc_info:
        appointment.cancel()

    errors = exc_info.value.errors()
    assert any("instance_id' is required" in str(e) for e in errors)


def test_appointment_invalid_note_type_category(
    mock_db_queries: dict[str, MagicMock], valid_appointment_data: dict[str, Any]
) -> None:
    """Test appointment with non-ENCOUNTER note type."""
    mock_note_type = mock_db_queries["note_type"]
    mock_note_type.values_list.return_value.get.return_value = (
        NoteTypeCategories.SCHEDULE_EVENT,
        True,
    )

    appointment = Appointment(**valid_appointment_data)

    with pytest.raises(ValidationError) as exc_info:
        appointment.create()

    errors = exc_info.value.errors()
    assert any("must be of type, encounter" in str(e) for e in errors)


def test_appointment_note_type_not_scheduleable(
    mock_db_queries: dict[str, MagicMock], valid_appointment_data: dict[str, Any]
) -> None:
    """Test appointment with non-scheduleable note type."""
    mock_note_type = mock_db_queries["note_type"]
    mock_note_type.values_list.return_value.get.return_value = (
        NoteTypeCategories.ENCOUNTER,
        False,  # Not scheduleable
    )

    appointment = Appointment(**valid_appointment_data)

    with pytest.raises(ValidationError) as exc_info:
        appointment.create()

    errors = exc_info.value.errors()
    assert any("Appointment note type must be scheduleable" in str(e) for e in errors)


def test_appointment_note_type_does_not_exist(
    mock_db_queries: dict[str, MagicMock], valid_appointment_data: dict[str, Any]
) -> None:
    """Test when note type doesn't exist."""
    mock_note_type = mock_db_queries["note_type"]
    mock_note_type.values_list.return_value.get.side_effect = NoteType.DoesNotExist

    appointment = Appointment(**valid_appointment_data)

    with pytest.raises(ValidationError) as exc_info:
        appointment.create()

    errors = exc_info.value.errors()
    assert any("Note type with ID" in str(e) and "does not exist" in str(e) for e in errors)


def test_appointment_external_identifiers(
    mock_db_queries: dict[str, MagicMock], valid_appointment_data: dict[str, Any]
) -> None:
    """Test appointment with external identifiers."""
    valid_appointment_data["external_identifiers"] = [
        AppointmentIdentifier(system="external", value="12345"),
        AppointmentIdentifier(system="other", value="67890"),
    ]

    appointment = Appointment(**valid_appointment_data)
    effect = appointment.create()

    payload = json.loads(effect.payload)
    assert len(payload["data"]["external_identifiers"]) == 2
    assert payload["data"]["external_identifiers"][0] == {"system": "external", "value": "12345"}
    assert payload["data"]["external_identifiers"][1] == {"system": "other", "value": "67890"}


def test_appointment_update_external_identifiers(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test updating external identifiers."""
    appointment = Appointment(instance_id=str(uuid4()))
    appointment.external_identifiers = [AppointmentIdentifier(system="updated", value="999")]
    appointment.start_time = datetime.datetime.now()  # Need at least one dirty field

    effect = appointment.update()

    payload = json.loads(effect.payload)
    # external_identifiers should be included even though it's excluded from dirty tracking
    assert "external_identifiers" in payload["data"]
    assert payload["data"]["external_identifiers"][0]["system"] == "updated"


def test_appointment_partial_update(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test updating only one field."""
    appointment = Appointment(instance_id=str(uuid4()))
    appointment.meeting_link = "https://updated-link.com"

    effect = appointment.update()
    payload = json.loads(effect.payload)

    # Should only contain instance_id and meeting_link
    assert set(payload["data"].keys()) == {"instance_id", "meeting_link"}
    assert payload["data"]["meeting_link"] == "https://updated-link.com"


def test_appointment_nonexistent_references(
    mock_db_queries: dict[str, MagicMock], valid_appointment_data: dict[str, Any]
) -> None:
    """Test validation when referenced entities don't exist."""
    mock_db_queries["patient"].filter.return_value.exists.return_value = False
    mock_db_queries["practice_location"].filter.return_value.exists.return_value = False

    appointment = Appointment(**valid_appointment_data)

    with pytest.raises(ValidationError) as exc_info:
        appointment.create()

    errors = exc_info.value.errors()
    error_messages = [str(e) for e in errors]
    assert any("Practice location with ID" in msg for msg in error_messages)
    assert any("Patient with ID" in msg for msg in error_messages)


def test_appointment_update_nonexistent_appointment(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test updating an appointment that doesn't exist."""
    mock_db_queries["appointment"].filter.return_value.exists.return_value = False

    appointment = Appointment(instance_id=str(uuid4()))
    appointment.start_time = datetime.datetime.now()

    with pytest.raises(ValidationError) as exc_info:
        appointment.update()

    errors = exc_info.value.errors()
    assert any("Appointment with ID" in str(e) and "does not exist" in str(e) for e in errors)


def test_create_appointment_parent_appointment_equals_instance_id(
    mock_db_queries: dict[str, MagicMock], valid_appointment_data: dict[str, Any]
) -> None:
    """Test that parent appointment cannot be the same as instance_id on creation."""
    same_id = str(uuid4())
    appointment_data = {
        **valid_appointment_data,
        "instance_id": same_id,
        "parent_appointment_id": same_id,
    }
    appointment = Appointment(**appointment_data)

    with pytest.raises(ValidationError) as exc_info:
        appointment.create()

    errors = exc_info.value.errors()
    assert any("parent_appointment_id cannot be the same as instance_id" in str(e) for e in errors)


def test_update_appointment_parent_appointment_equals_instance_id(
    mock_db_queries: dict[str, MagicMock], valid_appointment_data: dict[str, Any]
) -> None:
    """Test that parent appointment cannot be the same as instance_id on update."""
    same_id = str(uuid4())
    appointment_data = {
        **valid_appointment_data,
        "instance_id": same_id,
        "parent_appointment_id": same_id,
    }
    appointment = Appointment(**appointment_data)

    with pytest.raises(ValidationError) as exc_info:
        appointment.update()

    errors = exc_info.value.errors()
    assert any(
        "parent_appointment_id can only be set when creating an appointment." in str(e)
        for e in errors
    )


def test_appointment_reschedule_success(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test successful appointment reschedule."""
    appointment = Appointment(instance_id=str(uuid4()))
    appointment.start_time = datetime.datetime.now()
    appointment.duration_minutes = 45

    effect = appointment.reschedule()

    assert effect.type == EffectType.RESCHEDULE_APPOINTMENT
    payload = json.loads(effect.payload)
    assert "start_time" in payload["data"]
    assert payload["data"]["duration_minutes"] == 45


def test_appointment_reschedule_no_changes_fails(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that reschedule with no changes raises error."""
    appointment = Appointment(instance_id=str(uuid4()))

    with pytest.raises(ValueError) as exc_info:
        appointment.reschedule()

    assert "No fields have been modified" in str(exc_info.value)


def test_appointment_reschedule_missing_instance_id(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that reschedule without instance_id raises error."""
    appointment = Appointment(practice_location_id=str(uuid4()), provider_id=str(uuid4()))
    appointment.start_time = datetime.datetime.now()

    with pytest.raises(ValidationError) as exc_info:
        appointment.reschedule()

    errors = exc_info.value.errors()
    assert any("instance_id' is required" in str(e) for e in errors)


def test_appointment_reschedule_nonexistent_appointment(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test rescheduling an appointment that doesn't exist."""
    mock_db_queries["appointment"].filter.return_value.exists.return_value = False

    appointment = Appointment(instance_id=str(uuid4()))
    appointment.start_time = datetime.datetime.now()

    with pytest.raises(ValidationError) as exc_info:
        appointment.reschedule()

    errors = exc_info.value.errors()
    assert any("Appointment with ID" in str(e) and "does not exist" in str(e) for e in errors)


def test_appointment_reschedule_with_multiple_fields(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test rescheduling with multiple modified fields."""
    appointment = Appointment(instance_id=str(uuid4()))
    appointment.start_time = datetime.datetime.now()
    appointment.duration_minutes = 60
    appointment.meeting_link = "https://new-reschedule-link.com"

    effect = appointment.reschedule()

    assert effect.type == EffectType.RESCHEDULE_APPOINTMENT
    payload = json.loads(effect.payload)
    assert "start_time" in payload["data"]
    assert payload["data"]["duration_minutes"] == 60
    assert payload["data"]["meeting_link"] == "https://new-reschedule-link.com"


@pytest.fixture
def mock_appointment_label_queries() -> Generator[dict[str, MagicMock]]:
    """Mock database queries for appointment label effects."""
    with (
        patch("canvas_sdk.v1.data.appointment.AppointmentLabel.objects") as mock_appointment_label,
    ):
        # Setup default behaviors - using simplified query approach
        mock_appointment_label.filter.return_value.count.return_value = 0  # No existing labels

        yield {
            "appointment_label": mock_appointment_label,
        }


@pytest.fixture
def valid_appointment_label_data() -> dict[str, Any]:
    """Valid data for creating appointment label effects."""
    return {
        "appointment_id": str(uuid4()),
        "labels": {"MISSING_COVERAGE", "URGENT"},
    }


def test_add_appointment_label_values_property(
    valid_appointment_label_data: dict[str, Any],
) -> None:
    """Test that the values property returns the correct appointment_id and labels mapping."""
    from canvas_sdk.effects.note.appointment import AddAppointmentLabel

    effect = AddAppointmentLabel(**valid_appointment_label_data)
    expected_values = {
        "appointment_id": valid_appointment_label_data["appointment_id"],
        "labels": sorted(valid_appointment_label_data["labels"]),
    }
    assert effect.values == expected_values


def test_remove_appointment_label_values_property(
    valid_appointment_label_data: dict[str, Any],
) -> None:
    """Test that the values property returns the correct appointment_id and labels mapping."""
    from canvas_sdk.effects.note.appointment import RemoveAppointmentLabel

    effect = RemoveAppointmentLabel(**valid_appointment_label_data)
    expected_values = {
        "appointment_id": valid_appointment_label_data["appointment_id"],
        "labels": sorted(valid_appointment_label_data["labels"]),
    }
    assert effect.values == expected_values


@patch("canvas_sdk.v1.data.Appointment.objects")
def test_add_appointment_label_valid_appointment(
    mock_appointment: MagicMock, valid_appointment_label_data: dict[str, Any]
) -> None:
    """Test that no errors are returned if the appointment exists and label limit is not exceeded."""
    from canvas_sdk.effects.note.appointment import AddAppointmentLabel

    # Mock appointment exists with 1 existing label
    mock_filter = MagicMock()
    mock_annotate = MagicMock()
    mock_values_list = MagicMock()

    mock_appointment.filter.return_value = mock_filter
    mock_filter.annotate.return_value = mock_annotate
    mock_annotate.values_list.return_value = mock_values_list
    mock_values_list.first.return_value = 1

    effect = AddAppointmentLabel(**valid_appointment_label_data)
    errors = effect._get_error_details(method=None)
    assert errors == []


@patch("canvas_sdk.v1.data.Appointment.objects")
def test_add_appointment_label_nonexistent_appointment(
    mock_appointment: MagicMock, valid_appointment_label_data: dict[str, Any]
) -> None:
    """Test that an error is returned if the appointment doesn't exist (annotate returns None)."""
    from canvas_sdk.effects.note.appointment import AddAppointmentLabel

    # Mock appointment doesn't exist - first() returns None
    mock_filter = MagicMock()
    mock_annotate = MagicMock()
    mock_values_list = MagicMock()

    mock_appointment.filter.return_value = mock_filter
    mock_filter.annotate.return_value = mock_annotate
    mock_annotate.values_list.return_value = mock_values_list
    mock_values_list.first.return_value = None

    effect = AddAppointmentLabel(**valid_appointment_label_data)
    with patch.object(
        effect, "_create_error_detail", return_value="error_detail"
    ) as mock_create_error:
        errors = effect._get_error_details(method=None)
        mock_create_error.assert_called_once_with(
            "value",
            f"Appointment {valid_appointment_label_data['appointment_id']} does not exist",
            valid_appointment_label_data["appointment_id"],
        )
        assert errors == [mock_create_error.return_value]


@patch("canvas_sdk.v1.data.Appointment.objects")
def test_add_appointment_label_limit_exceeded(
    mock_appointment: MagicMock, valid_appointment_label_data: dict[str, Any]
) -> None:
    """Test that an error is returned if adding labels would exceed the 3-label limit."""
    from canvas_sdk.effects.note.appointment import AddAppointmentLabel

    # Mock appointment exists with 2 existing labels
    mock_filter = MagicMock()
    mock_annotate = MagicMock()
    mock_values_list = MagicMock()

    mock_appointment.filter.return_value = mock_filter
    mock_filter.annotate.return_value = mock_annotate
    mock_annotate.values_list.return_value = mock_values_list
    mock_values_list.first.return_value = 2

    effect = AddAppointmentLabel(**valid_appointment_label_data)
    with patch.object(
        effect, "_create_error_detail", return_value="error_detail"
    ) as mock_create_error:
        errors = effect._get_error_details(method=None)
        mock_create_error.assert_called_once_with(
            "value",
            "Limit reached: Only 3 appointment labels allowed. Attempted to add 2 label(s) to appointment with 2 existing label(s).",
            sorted(valid_appointment_label_data["labels"]),
        )
        assert errors == [mock_create_error.return_value]


@patch("canvas_sdk.v1.data.Appointment.objects")
def test_add_appointment_label_valid_with_existing_labels(
    mock_appointment: MagicMock, valid_appointment_label_data: dict[str, Any]
) -> None:
    """Test that no errors are returned when adding labels within the limit."""
    from canvas_sdk.effects.note.appointment import AddAppointmentLabel

    # Mock appointment exists with 1 existing label
    mock_filter = MagicMock()
    mock_annotate = MagicMock()
    mock_values_list = MagicMock()

    mock_appointment.filter.return_value = mock_filter
    mock_filter.annotate.return_value = mock_annotate
    mock_annotate.values_list.return_value = mock_values_list
    mock_values_list.first.return_value = 1

    effect = AddAppointmentLabel(**valid_appointment_label_data)
    errors = effect._get_error_details(method=None)
    assert errors == []


def test_remove_appointment_label_valid_appointment(
    valid_appointment_label_data: dict[str, Any],
) -> None:
    """Test that no errors are returned for remove operation (no validation needed)."""
    from canvas_sdk.effects.note.appointment import RemoveAppointmentLabel

    effect = RemoveAppointmentLabel(**valid_appointment_label_data)
    errors = effect._get_error_details(method=None)
    assert errors == []


def test_create_appointment_with_labels(
    mock_db_queries: dict[str, MagicMock], valid_appointment_data: dict[str, Any]
) -> None:
    """Test creating an appointment with labels."""
    valid_appointment_data["labels"] = {"MISSING_COVERAGE", "URGENT"}

    appointment = Appointment(**valid_appointment_data)
    effect = appointment.create()

    assert effect.type == EffectType.CREATE_APPOINTMENT
    payload = json.loads(effect.payload)
    assert payload["data"]["labels"] == sorted(["MISSING_COVERAGE", "URGENT"])


def test_create_appointment_with_too_many_labels(
    mock_db_queries: dict[str, MagicMock], valid_appointment_data: dict[str, Any]
) -> None:
    """Test creating an appointment with more than 3 labels fails."""
    valid_appointment_data["labels"] = {"LABEL1", "LABEL2", "LABEL3", "LABEL4"}

    with pytest.raises(ValidationError) as exc_info:
        Appointment(**valid_appointment_data)

    errors = exc_info.value.errors()
    assert any("at most 3 items" in str(e) for e in errors)


def test_create_appointment_with_invalid_label_length(
    mock_db_queries: dict[str, MagicMock], valid_appointment_data: dict[str, Any]
) -> None:
    """Test creating an appointment with labels that are too long."""
    valid_appointment_data["labels"] = {"A" * 51}  # 51 characters, exceeds max_length=50

    with pytest.raises(ValidationError) as exc_info:
        Appointment(**valid_appointment_data)

    errors = exc_info.value.errors()
    assert any("at most 50 characters" in str(e) for e in errors)


@patch("canvas_sdk.v1.data.appointment.AppointmentLabel.objects")
@patch("canvas_sdk.v1.data.appointment.Appointment.objects")
def test_update_appointment_with_labels(
    mock_appointment: MagicMock, mock_appointment_label: MagicMock
) -> None:
    """Test updating an appointment with labels."""
    mock_appointment.filter.return_value.exists.return_value = True
    mock_appointment_label.filter.return_value.count.return_value = 0

    appointment = Appointment(instance_id=str(uuid4()))
    appointment.labels = {"UPDATED_LABEL"}

    effect = appointment.update()

    assert effect.type == EffectType.UPDATE_APPOINTMENT
    payload = json.loads(effect.payload)
    assert payload["data"]["labels"] == sorted(["UPDATED_LABEL"])


@patch("canvas_sdk.v1.data.appointment.AppointmentLabel.objects")
@patch("canvas_sdk.v1.data.appointment.Appointment.objects")
def test_appointment_label_validation_exceeds_limit(
    mock_appointment: MagicMock, mock_appointment_label: MagicMock
) -> None:
    """Test that updating an appointment with labels that would exceed the 3-label limit fails."""
    mock_appointment.filter.return_value.exists.return_value = True
    mock_appointment_label.filter.return_value.count.return_value = 2

    appointment = Appointment(instance_id=str(uuid4()))
    appointment.labels = {"LABEL1", "LABEL2"}  # Would make total 4 labels

    with pytest.raises(ValidationError) as exc_info:
        appointment.update()

    errors = exc_info.value.errors()
    assert any("Limit reached: Only 3 appointment labels allowed" in str(e) for e in errors)
