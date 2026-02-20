import json
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from pydantic_core import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.note import Note


@pytest.fixture
def mock_note_exists() -> Generator[MagicMock]:
    """Mock Note.objects to simulate an existing note."""
    with patch("canvas_sdk.effects.note_metadata.base.Note.objects") as mock_note:
        mock_note.filter.return_value.exists.return_value = True
        yield mock_note


@pytest.fixture
def mock_note_not_exists() -> Generator[MagicMock]:
    """Mock Note.objects to simulate a non-existing note."""
    with patch("canvas_sdk.effects.note_metadata.base.Note.objects") as mock_note:
        mock_note.filter.return_value.exists.return_value = False
        yield mock_note


def test_upsert_metadata_creates_effect_with_correct_type(mock_note_exists: MagicMock) -> None:
    """Test that upsert_metadata creates an Effect with the correct type."""
    note = Note(instance_id="test-note-id")
    effect = note.upsert_metadata(key="test_key", value="test_value")

    assert effect.type == EffectType.UPSERT_NOTE_METADATA


def test_upsert_metadata_creates_effect_with_correct_payload(mock_note_exists: MagicMock) -> None:
    """Test that upsert_metadata creates an Effect with the correct payload structure."""
    note = Note(instance_id="test-note-id")
    effect = note.upsert_metadata(key="test_key", value="test_value")

    payload = json.loads(effect.payload)
    assert payload == {
        "data": {
            "note_id": "test-note-id",
            "key": "test_key",
            "value": "test_value",
        }
    }


def test_upsert_metadata_fails_when_note_does_not_exist(
    mock_note_not_exists: MagicMock,
) -> None:
    """Test that upsert_metadata validates the note exists."""
    note = Note(instance_id="nonexistent-note-id")

    with pytest.raises(ValidationError) as exc_info:
        note.upsert_metadata(key="test_key", value="test_value")

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert "nonexistent-note-id" in errors[0]["msg"]


def test_upsert_metadata_passes_when_note_exists(mock_note_exists: MagicMock) -> None:
    """Test that upsert_metadata succeeds when the note exists."""
    note = Note(instance_id="existing-note-id")

    effect = note.upsert_metadata(key="test_key", value="test_value")
    assert effect is not None


def test_upsert_metadata_fails_without_instance_id() -> None:
    """Test that upsert_metadata raises ValueError when instance_id is not set."""
    note = Note()

    with pytest.raises(ValueError, match="instance_id"):
        note.upsert_metadata(key="test_key", value="test_value")
