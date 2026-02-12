import json
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from pydantic_core import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.note_metadata import NoteMetadata


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


def test_upsert_creates_effect_with_correct_type(mock_note_exists: MagicMock) -> None:
    """Test that upsert creates an Effect with the correct type string."""
    metadata = NoteMetadata(note_id="test-note-id", key="test_key")
    effect = metadata.upsert("test_value")

    assert effect.type == EffectType.UPSERT_NOTE_METADATA


def test_upsert_creates_effect_with_correct_payload(mock_note_exists: MagicMock) -> None:
    """Test that upsert creates an Effect with the correct payload structure."""
    metadata = NoteMetadata(note_id="test-note-id", key="test_key")
    effect = metadata.upsert("test_value")

    payload = json.loads(effect.payload)
    assert payload == {
        "data": {
            "note_id": "test-note-id",
            "key": "test_key",
            "value": "test_value",
        }
    }


def test_validation_fails_when_note_does_not_exist(mock_note_not_exists: MagicMock) -> None:
    """Test that validation fails when the note doesn't exist."""
    metadata = NoteMetadata(note_id="nonexistent-note-id", key="test_key")

    with pytest.raises(ValidationError) as exc_info:
        metadata.upsert("test_value")

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert "nonexistent-note-id" in errors[0]["msg"]


def test_validation_passes_when_note_exists(mock_note_exists: MagicMock) -> None:
    """Test that validation passes when the note exists."""
    metadata = NoteMetadata(note_id="existing-note-id", key="test_key")

    effect = metadata.upsert("test_value")
    assert effect is not None
