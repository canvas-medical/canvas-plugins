import json
from collections.abc import Generator
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from pydantic_core import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.note.freeze import _FreezeNoteEffect, _UnfreezeNoteEffect


@pytest.fixture
def mock_db_queries() -> Generator[dict[str, MagicMock]]:
    """Mock database queries for note and staff existence checks."""
    with (
        patch("canvas_sdk.effects.note.freeze.Note.objects") as mock_note,
        patch("canvas_sdk.effects.note.freeze.Staff.objects") as mock_staff,
    ):
        mock_note.filter.return_value.exists.return_value = True
        mock_staff.filter.return_value.exists.return_value = True

        yield {
            "note": mock_note,
            "staff": mock_staff,
        }


def test_freeze_note_effect_success(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test successful freeze note effect creation."""
    note_id = uuid4()
    effect = _FreezeNoteEffect(note_id=note_id, duration=60)
    applied = effect.apply()

    assert applied.type == EffectType.FREEZE_NOTE
    payload = json.loads(applied.payload)
    assert payload["data"]["note_id"] == str(note_id)
    assert payload["data"]["duration"] == 60


def test_freeze_note_effect_default_duration(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test freeze note effect with default duration."""
    note_id = uuid4()
    effect = _FreezeNoteEffect(note_id=note_id)
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["duration"] == 300


def test_freeze_note_effect_invalid_duration() -> None:
    """Test freeze note effect with invalid duration raises validation error."""
    note_id = uuid4()
    with pytest.raises(ValidationError) as exc_info:
        _FreezeNoteEffect(note_id=note_id, duration=0)

    errors = exc_info.value.errors()
    assert any("duration" in str(e["loc"]) for e in errors)


def test_freeze_note_effect_negative_duration() -> None:
    """Test freeze note effect with negative duration raises validation error."""
    note_id = uuid4()
    with pytest.raises(ValidationError) as exc_info:
        _FreezeNoteEffect(note_id=note_id, duration=-1)

    errors = exc_info.value.errors()
    assert any("duration" in str(e["loc"]) for e in errors)


def test_freeze_note_effect_uuid_object(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test freeze note effect accepts UUID object."""
    note_id = uuid4()
    effect = _FreezeNoteEffect(note_id=note_id, duration=120)
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["note_id"] == str(note_id)


def test_freeze_note_effect_payload_structure(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test freeze note effect payload has correct structure."""
    note_id = uuid4()
    effect = _FreezeNoteEffect(note_id=note_id, duration=60)
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert "data" in payload
    assert "note_id" in payload["data"]
    assert "duration" in payload["data"]


def test_freeze_note_effect_with_user_id(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test freeze note effect with user_id."""
    note_id = uuid4()
    user_id = "staff-key-123"
    effect = _FreezeNoteEffect(note_id=note_id, duration=60, user_id=user_id)
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["user_id"] == user_id


def test_freeze_note_effect_without_user_id(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test freeze note effect without user_id doesn't include it in payload."""
    note_id = uuid4()
    effect = _FreezeNoteEffect(note_id=note_id, duration=60)
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert "user_id" not in payload["data"]


def test_freeze_note_effect_string_note_id(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test freeze note effect accepts string note_id."""
    note_id = uuid4()
    effect = _FreezeNoteEffect(note_id=str(note_id), duration=60)
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["note_id"] == str(note_id)


def test_freeze_note_does_not_exist(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test freeze raises validation error when note does not exist."""
    mock_db_queries["note"].filter.return_value.exists.return_value = False

    note_id = uuid4()
    effect = _FreezeNoteEffect(note_id=note_id, duration=60)

    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    errors = exc_info.value.errors()
    msgs = [e["msg"] for e in errors]
    assert f"Note with ID {note_id} does not exist." in msgs


def test_freeze_staff_does_not_exist(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test freeze raises validation error when staff does not exist."""
    mock_db_queries["staff"].filter.return_value.exists.return_value = False

    note_id = uuid4()
    effect = _FreezeNoteEffect(note_id=note_id, duration=60, user_id="nonexistent-staff")

    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    errors = exc_info.value.errors()
    msgs = [e["msg"] for e in errors]
    assert "Staff with ID nonexistent-staff does not exist." in msgs


def test_freeze_note_and_staff_do_not_exist(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test freeze collects both note and staff validation errors."""
    mock_db_queries["note"].filter.return_value.exists.return_value = False
    mock_db_queries["staff"].filter.return_value.exists.return_value = False

    note_id = uuid4()
    effect = _FreezeNoteEffect(note_id=note_id, duration=60, user_id="bad-staff")

    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    errors = exc_info.value.errors()
    msgs = [e["msg"] for e in errors]
    assert f"Note with ID {note_id} does not exist." in msgs
    assert "Staff with ID bad-staff does not exist." in msgs


def test_unfreeze_note_effect_success(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test successful unfreeze note effect creation."""
    note_id = uuid4()
    effect = _UnfreezeNoteEffect(note_id=note_id)
    applied = effect.apply()

    assert applied.type == EffectType.UNFREEZE_NOTE
    payload = json.loads(applied.payload)
    assert payload["data"]["note_id"] == str(note_id)


def test_unfreeze_note_effect_string_note_id(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test unfreeze note effect accepts string note_id."""
    note_id = uuid4()
    effect = _UnfreezeNoteEffect(note_id=str(note_id))
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["note_id"] == str(note_id)


def test_unfreeze_note_effect_uuid_object(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test unfreeze note effect accepts UUID object."""
    note_id = uuid4()
    effect = _UnfreezeNoteEffect(note_id=note_id)
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["note_id"] == str(note_id)


def test_unfreeze_note_effect_payload_structure(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test unfreeze note effect payload has correct structure."""
    note_id = uuid4()
    effect = _UnfreezeNoteEffect(note_id=note_id)
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert "data" in payload
    assert "note_id" in payload["data"]
    assert "duration" not in payload["data"]


def test_unfreeze_note_does_not_exist(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test unfreeze raises validation error when note does not exist."""
    mock_db_queries["note"].filter.return_value.exists.return_value = False

    note_id = uuid4()
    effect = _UnfreezeNoteEffect(note_id=note_id)

    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    errors = exc_info.value.errors()
    msgs = [e["msg"] for e in errors]
    assert f"Note with ID {note_id} does not exist." in msgs
