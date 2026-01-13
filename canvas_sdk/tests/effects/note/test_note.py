import datetime
import json
from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from pydantic_core import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.note.note import Note
from canvas_sdk.v1.data.note import NoteStates, NoteTypeCategories


@pytest.fixture
def mock_db_queries() -> Generator[dict[str, MagicMock]]:
    """Mock all database queries to return True/exist by default."""
    with (
        patch("canvas_sdk.v1.data.PracticeLocation.objects") as mock_pl,
        patch("canvas_sdk.v1.data.Staff.objects") as mock_staff,
        patch("canvas_sdk.v1.data.Patient.objects") as mock_patient,
        patch("canvas_sdk.v1.data.Note.objects") as mock_note,
        patch("canvas_sdk.v1.data.NoteType.objects") as mock_note_type,
    ):
        # Setup default behaviors
        mock_pl.filter.return_value.exists.return_value = True
        mock_staff.filter.return_value.exists.return_value = True
        mock_patient.filter.return_value.exists.return_value = True
        mock_note.filter.return_value.exists.return_value = True

        # Note type default behavior
        mock_note_type.values_list.return_value.filter.return_value.first.return_value = (
            NoteTypeCategories.ENCOUNTER
        )

        yield {
            "practice_location": mock_pl,
            "staff": mock_staff,
            "patient": mock_patient,
            "note": mock_note,
            "note_type": mock_note_type,
        }


@pytest.fixture
def valid_note_data() -> dict[str, Any]:
    """Valid data for creating a Note."""
    return {
        "practice_location_id": str(uuid4()),
        "provider_id": str(uuid4()),
        "note_type_id": str(uuid4()),
        "datetime_of_service": datetime.datetime.now(),
        "patient_id": str(uuid4()),
        "title": "Test Note",
    }


def test_create_note_success(
    mock_db_queries: dict[str, MagicMock], valid_note_data: dict[str, Any]
) -> None:
    """Test successful note creation."""
    note = Note(**valid_note_data)
    effect = note.create()
    assert effect.type == EffectType.CREATE_NOTE
    payload = json.loads(effect.payload)
    assert payload["data"]["note_type_id"] == valid_note_data["note_type_id"]
    assert payload["data"]["patient_id"] == valid_note_data["patient_id"]
    assert payload["data"]["title"] == "Test Note"
    assert "instance_id" not in payload["data"]


def test_create_note_missing_required_fields(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test note creation with missing required fields."""
    note = Note(practice_location_id=str(uuid4()), provider_id=str(uuid4()))

    with pytest.raises(ValidationError) as exc_info:
        note.create()

    errors = exc_info.value.errors()
    error_fields = [e["msg"] for e in errors]
    assert "Field 'note_type_id' is required to create a note." in error_fields
    assert "Field 'datetime_of_service' is required to create a note." in error_fields
    assert "Field 'patient_id' is required to create a note." in error_fields


def test_create_note_with_instance_id_passes(
    mock_db_queries: dict[str, MagicMock], valid_note_data: dict[str, Any]
) -> None:
    """Test that providing instance_id for create does not raise error."""
    mock_db_queries["note"].filter.return_value.exists.return_value = False

    valid_note_data["instance_id"] = str(uuid4())
    note = Note(**valid_note_data)

    effect = note.create()
    assert effect.type == EffectType.CREATE_NOTE

    payload = json.loads(effect.payload)
    assert payload["data"]["instance_id"] == note.instance_id


def test_note_update_success(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test successful note update."""
    note = Note(instance_id=str(uuid4()))
    note.title = "Updated Title"
    note.datetime_of_service = datetime.datetime.now()

    effect = note.update()

    assert effect.type == EffectType.UPDATE_NOTE
    payload = json.loads(effect.payload)
    assert payload["data"]["title"] == "Updated Title"
    assert "datetime_of_service" in payload["data"]
    # Should not include unchanged fields
    assert "patient_id" not in payload["data"]
    assert "note_type_id" not in payload["data"]


def test_note_update_prevents_changing_immutable_fields(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that updating note_type_id or patient_id raises error."""
    note = Note(instance_id=str(uuid4()))
    note.note_type_id = str(uuid4())
    note.patient_id = str(uuid4())

    with pytest.raises(ValidationError) as exc_info:
        note.update()

    errors = exc_info.value.errors()
    error_messages = [str(e) for e in errors]
    assert any("note_type_id' cannot be updated" in msg for msg in error_messages)
    assert any("patient_id' cannot be updated" in msg for msg in error_messages)


def test_note_update_no_changes_fails(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that update with no changes raises error."""
    note = Note(instance_id=str(uuid4()))
    with pytest.raises(ValueError) as exc_info:
        note.update()

    assert "No fields have been modified" in str(exc_info.value)


def test_note_update_missing_instance_id(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that update without instance_id raises error."""
    note = Note(practice_location_id=str(uuid4()), provider_id=str(uuid4()))
    note.title = "New Title"

    with pytest.raises(ValidationError) as exc_info:
        note.update()

    errors = exc_info.value.errors()
    assert any("instance_id' is required to update" in str(e) for e in errors)


def test_note_nonexistent_references(
    mock_db_queries: dict[str, MagicMock], valid_note_data: dict[str, Any]
) -> None:
    """Test validation when referenced entities don't exist."""
    mock_db_queries["patient"].filter.return_value.exists.return_value = False
    mock_db_queries["practice_location"].filter.return_value.exists.return_value = False
    mock_db_queries["staff"].filter.return_value.exists.return_value = False

    note = Note(**valid_note_data)

    with pytest.raises(ValidationError) as exc_info:
        note.create()

    errors = exc_info.value.errors()
    error_messages = [str(e) for e in errors]
    assert any("Practice location with ID" in msg for msg in error_messages)
    assert any("Patient with ID" in msg for msg in error_messages)
    assert any("Provider with ID" in msg for msg in error_messages)


def test_note_nonexistent_note_type(
    mock_db_queries: dict[str, MagicMock], valid_note_data: dict[str, Any]
) -> None:
    """Test when note type doesn't exist."""
    mock_note_type = mock_db_queries["note_type"]
    mock_note_type.values_list.return_value.filter.return_value.first.return_value = None

    note = Note(**valid_note_data)

    with pytest.raises(ValidationError) as exc_info:
        note.create()

    errors = exc_info.value.errors()
    assert any("Note type with ID" in str(e) and "does not exist" in str(e) for e in errors)


def test_note_create_existing_note(
    mock_db_queries: dict[str, MagicMock], valid_note_data: dict[str, Any]
) -> None:
    """Test creating a note that already exists."""
    mock_db_queries["note"].filter.return_value.exists.return_value = True

    note = Note(instance_id=str(uuid4()))
    note.title = "New Note"

    with pytest.raises(ValidationError) as exc_info:
        note.create()

    errors = exc_info.value.errors()
    assert any("Note with ID" in str(e) and "already exists" in str(e) for e in errors)


def test_note_update_nonexistent_note(
    mock_db_queries: dict[str, MagicMock], valid_note_data: dict[str, Any]
) -> None:
    """Test updating a note that doesn't exist."""
    mock_db_queries["note"].filter.return_value.exists.return_value = False

    note = Note(instance_id=str(uuid4()))
    note.title = "Updated"

    with pytest.raises(ValidationError) as exc_info:
        note.update()

    errors = exc_info.value.errors()
    assert any("Note with ID" in str(e) and "does not exist" in str(e) for e in errors)


def test_note_all_prohibited_categories_rejected(
    mock_db_queries: dict[str, MagicMock], valid_note_data: dict[str, Any]
) -> None:
    """Test that all prohibited note type categories are rejected."""
    prohibited_categories = [
        NoteTypeCategories.APPOINTMENT,
        NoteTypeCategories.SCHEDULE_EVENT,
        NoteTypeCategories.MESSAGE,
        NoteTypeCategories.LETTER,
    ]

    for category in prohibited_categories:
        mock_note_type = mock_db_queries["note_type"]
        mock_note_type.values_list.return_value.filter.return_value.first.return_value = category

        note = Note(**valid_note_data)

        with pytest.raises(ValidationError) as exc_info:
            note.create()

        errors = exc_info.value.errors()
        assert any(f"Visit note type cannot be of type: {category}" in str(e) for e in errors)


def test_note_update_only_allowed_fields(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that only title and datetime_of_service can be updated."""
    instance_id = str(uuid4())
    note = Note(instance_id=instance_id)

    # These should work
    note.title = "Updated Title"
    note.datetime_of_service = datetime.datetime(2024, 1, 1, 10, 0)

    effect = note.update()
    payload = json.loads(effect.payload)

    # Check that only the changed fields and instance_id are in payload
    assert set(payload["data"].keys()) == {"instance_id", "title", "datetime_of_service"}
    assert payload["data"]["title"] == "Updated Title"
    assert payload["data"]["datetime_of_service"] == "2024-01-01T10:00:00"


def test_note_partial_update(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test updating only one field."""
    note = Note(instance_id=str(uuid4()))
    note.title = "Only Title Updated"

    effect = note.update()
    payload = json.loads(effect.payload)

    # Should only contain instance_id and title
    assert set(payload["data"].keys()) == {"instance_id", "title"}
    assert payload["data"]["title"] == "Only Title Updated"


def test_note_create_with_all_fields(
    mock_db_queries: dict[str, MagicMock], valid_note_data: dict[str, Any]
) -> None:
    """Test creating a note with all possible fields."""
    note = Note(**valid_note_data)
    effect = note.create()

    payload = json.loads(effect.payload)
    expected_fields = {
        "practice_location_id",
        "provider_id",
        "note_type_id",
        "datetime_of_service",
        "patient_id",
        "title",
    }
    assert set(payload["data"].keys()) == expected_fields

    # Verify datetime is serialized as ISO format string
    assert isinstance(payload["data"]["datetime_of_service"], str)


def test_note_create_without_optional_title(
    mock_db_queries: dict[str, MagicMock], valid_note_data: dict[str, Any]
) -> None:
    """Test creating a note without the optional title field."""
    del valid_note_data["title"]

    note = Note(**valid_note_data)
    effect = note.create()

    payload = json.loads(effect.payload)
    assert "title" not in payload["data"]
    assert effect.type == EffectType.CREATE_NOTE


def test_note_multiple_validation_errors(
    mock_db_queries: dict[str, MagicMock], valid_note_data: dict[str, Any]
) -> None:
    """Test that multiple validation errors are collected and reported together."""
    # Make all validations fail
    mock_db_queries["practice_location"].filter.return_value.exists.return_value = False
    mock_db_queries["staff"].filter.return_value.exists.return_value = False

    note = Note(
        practice_location_id=str(uuid4()),
        provider_id=str(uuid4()),
        # Missing required fields
    )

    with pytest.raises(ValidationError) as exc_info:
        note.create()

    errors = exc_info.value.errors()
    error_messages = [e["msg"] for e in errors]

    # Should have errors for:
    # - 3 missing required fields (note_type_id, datetime_of_service, patient_id)
    # - 2 invalid references (practice_location, provider)
    assert len(errors) == 5

    # Check specific error messages
    assert "Field 'note_type_id' is required to create a note." in error_messages
    assert "Field 'datetime_of_service' is required to create a note." in error_messages
    assert "Field 'patient_id' is required to create a note." in error_messages
    assert any("Practice location with ID" in msg for msg in error_messages)
    assert any("Provider with ID" in msg for msg in error_messages)


def test_push_charges_missing_instance_id(mock_db_queries: dict[str, MagicMock]) -> None:
    """push_charges should require an instance_id before attempting to push."""
    note = Note()

    with pytest.raises(ValidationError) as exc_info:
        note.push_charges()

    errors = exc_info.value.errors()
    msgs = [e["msg"] for e in errors]
    assert "Field 'instance_id' is required." in msgs


def test_push_charges_note_does_not_exist(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """If the note instance_id does not match a persisted Note, raise a ValidationError."""
    instance_id = str(uuid4())
    # Ensure the DB returns no note for this id
    mock_db_queries["note"].filter.return_value.first.return_value = None

    note = Note(instance_id=instance_id)

    with pytest.raises(ValidationError) as exc_info:
        note.push_charges()

    errors = exc_info.value.errors()
    msgs = [e["msg"] for e in errors]
    assert f"Note with ID {instance_id} does not exist." in msgs


def test_push_charges_note_not_billable(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """If the note exists but its note_type_version is not billable, raise a ValidationError."""
    instance_id = str(uuid4())

    # create a fake persisted note with a non-billable note_type_version
    fake_note = MagicMock()
    fake_note.note_type_version = MagicMock(is_billable=False)
    mock_db_queries["note"].filter.return_value.first.return_value = fake_note

    note = Note(instance_id=instance_id)

    with pytest.raises(ValidationError) as exc_info:
        note.push_charges()

    errors = exc_info.value.errors()
    msgs = [e["msg"] for e in errors]
    # message includes that the note type is not billable
    assert any("is not billable and has no associated claim" in m for m in msgs)


def test_push_charges_success(mock_db_queries: dict[str, MagicMock]) -> None:
    """When the note exists and is billable, push_charges returns a PUSH_NOTE_CHARGES effect."""
    instance_id = str(uuid4())

    fake_note = MagicMock()
    fake_note.note_type_version = MagicMock(is_billable=True)
    fake_note.current_state = MagicMock(state=NoteStates.NEW)
    mock_db_queries["note"].filter.return_value.first.return_value = fake_note

    note = Note(instance_id=instance_id)
    effect = note.push_charges()

    assert effect.type == EffectType.PUSH_NOTE_CHARGES
    payload = json.loads(effect.payload)
    assert payload["data"]["note"] == instance_id


def test_lock_note_missing_instance_id(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that lock requires an instance_id."""
    note = Note()

    with pytest.raises(ValidationError) as exc_info:
        note.lock()

    errors = exc_info.value.errors()
    msgs = [e["msg"] for e in errors]
    assert "Field 'instance_id' is required." in msgs


def test_lock_note_does_not_exist(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that lock fails when the note does not exist."""
    instance_id = str(uuid4())
    mock_db_queries["note"].filter.return_value.first.return_value = None

    note = Note(instance_id=instance_id)

    with pytest.raises(ValidationError) as exc_info:
        note.lock()

    errors = exc_info.value.errors()
    msgs = [e["msg"] for e in errors]
    assert f"Note with ID {instance_id} does not exist." in msgs


def test_sign_note_missing_instance_id(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that sign requires an instance_id."""
    note = Note()

    with pytest.raises(ValidationError) as exc_info:
        note.sign()

    errors = exc_info.value.errors()
    msgs = [e["msg"] for e in errors]
    assert "Field 'instance_id' is required." in msgs


def test_sign_note_does_not_exist(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that sign fails when the note does not exist."""
    instance_id = str(uuid4())
    mock_db_queries["note"].filter.return_value.first.return_value = None

    note = Note(instance_id=instance_id)

    with pytest.raises(ValidationError) as exc_info:
        note.sign()

    errors = exc_info.value.errors()
    msgs = [e["msg"] for e in errors]
    assert f"Note with ID {instance_id} does not exist." in msgs


def test_sign_note_no_signature_required(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that sign fails when the note type does not require a signature."""
    instance_id = str(uuid4())

    fake_note = MagicMock()
    fake_note.current_state = MagicMock(state=NoteStates.LOCKED)
    fake_note.note_type_version = MagicMock(is_sig_required=False)
    mock_db_queries["note"].filter.return_value.first.return_value = fake_note

    note = Note(instance_id=instance_id)

    with pytest.raises(ValidationError) as exc_info:
        note.sign()

    errors = exc_info.value.errors()
    msgs = [e["msg"] for e in errors]
    assert "Cannot sign a note that does not require a signature." in msgs


def test_lock_success(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test successful note lock."""
    instance_id = str(uuid4())

    fake_note = MagicMock()
    fake_note.current_state = MagicMock(state=NoteStates.NEW)
    fake_note.note_type_version = MagicMock(
        name="Visit Note", category=NoteTypeCategories.ENCOUNTER
    )
    mock_db_queries["note"].filter.return_value.first.return_value = fake_note

    note = Note(instance_id=instance_id)
    effect = note.lock()

    assert effect.type == EffectType.LOCK_NOTE
    payload = json.loads(effect.payload)
    assert payload["data"]["note"] == instance_id


def test_unlock_success(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test successful note unlock."""
    instance_id = str(uuid4())

    fake_note = MagicMock()
    fake_note.current_state = MagicMock(state=NoteStates.LOCKED)
    fake_note.note_type_version = MagicMock(
        name="Visit Note", category=NoteTypeCategories.ENCOUNTER
    )
    mock_db_queries["note"].filter.return_value.first.return_value = fake_note

    note = Note(instance_id=instance_id)
    effect = note.unlock()

    assert effect.type == EffectType.UNLOCK_NOTE
    payload = json.loads(effect.payload)
    assert payload["data"]["note"] == instance_id


def test_sign_success(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test successful note sign."""
    instance_id = str(uuid4())

    fake_note = MagicMock()
    fake_note.current_state = MagicMock(state=NoteStates.LOCKED)
    fake_note.note_type_version = MagicMock(
        name="Visit Note", category=NoteTypeCategories.ENCOUNTER, is_sig_required=True
    )
    mock_db_queries["note"].filter.return_value.first.return_value = fake_note

    note = Note(instance_id=instance_id)
    effect = note.sign()

    assert effect.type == EffectType.SIGN_NOTE
    payload = json.loads(effect.payload)
    assert payload["data"]["note"] == instance_id


@pytest.mark.parametrize(
    "category",
    [NoteTypeCategories.MESSAGE, NoteTypeCategories.LETTER],
    ids=[
        "message",
        "category",
    ],
)
def test_note_state_change_unsupported_note_type(
    mock_db_queries: dict[str, MagicMock], category: NoteTypeCategories
) -> None:
    """Test that state changes are rejected for unsupported note types."""
    instance_id = str(uuid4())

    fake_note = MagicMock()
    fake_note.current_state = MagicMock(state=NoteStates.NEW)
    fake_note.note_type_version = MagicMock(name=category, category=category)
    mock_db_queries["note"].filter.return_value.first.return_value = fake_note

    note = Note(instance_id=instance_id)

    with pytest.raises(ValidationError) as exc_info:
        note.lock()

    errors = exc_info.value.errors()
    msgs = [e["msg"] for e in errors]
    assert any(
        f"Note with note type {fake_note.note_type_version.name} cannot perform action 'lock'." in m
        for m in msgs
    )


def test_check_in_note_not_appointment(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that check_in raises an error when the note is not an appointment."""
    instance_id = str(uuid4())

    fake_note = MagicMock()
    fake_note.current_state = MagicMock(state=NoteStates.NEW)
    fake_note.note_type_version = MagicMock(
        name="Visit Note", category=NoteTypeCategories.ENCOUNTER
    )
    mock_db_queries["note"].filter.return_value.first.return_value = fake_note

    note = Note(instance_id=instance_id)

    with pytest.raises(ValidationError) as exc_info:
        note.check_in()

    errors = exc_info.value.errors()
    msgs = [e["msg"] for e in errors]
    assert "Only appointments can be checked in or marked as no-show." in msgs


def test_no_show_note_not_appointment(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that no_show raises an error when the note is not an appointment."""
    instance_id = str(uuid4())

    fake_note = MagicMock()
    fake_note.current_state = MagicMock(state=NoteStates.NEW)
    fake_note.note_type_version = MagicMock(
        name="Visit Note", category=NoteTypeCategories.ENCOUNTER
    )
    mock_db_queries["note"].filter.return_value.first.return_value = fake_note

    note = Note(instance_id=instance_id)

    with pytest.raises(ValidationError) as exc_info:
        note.no_show()

    errors = exc_info.value.errors()
    msgs = [e["msg"] for e in errors]
    assert "Only appointments can be checked in or marked as no-show." in msgs


def test_check_in_success(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test successful check_in for an appointment."""
    instance_id = str(uuid4())

    fake_note = MagicMock()
    fake_note.current_state = MagicMock(state=NoteStates.NEW)
    fake_note.note_type_version = MagicMock(
        name="Appointment", category=NoteTypeCategories.APPOINTMENT
    )
    mock_db_queries["note"].filter.return_value.first.return_value = fake_note

    note = Note(instance_id=instance_id)
    effect = note.check_in()

    assert effect.type == EffectType.CHECK_IN_NOTE
    payload = json.loads(effect.payload)
    assert payload["data"]["note"] == instance_id


def test_no_show_success(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test successful no_show for an appointment."""
    instance_id = str(uuid4())

    fake_note = MagicMock()
    fake_note.current_state = MagicMock(state=NoteStates.NEW)
    fake_note.note_type_version = MagicMock(
        name="Appointment", category=NoteTypeCategories.APPOINTMENT
    )
    mock_db_queries["note"].filter.return_value.first.return_value = fake_note

    note = Note(instance_id=instance_id)
    effect = note.no_show()

    assert effect.type == EffectType.NO_SHOW_NOTE
    payload = json.loads(effect.payload)
    assert payload["data"]["note"] == instance_id
