import json
from uuid import uuid4

import pytest
from pydantic_core import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.note.freeze import FreezeNoteEffect, UnfreezeNoteEffect


def test_freeze_note_effect_success() -> None:
    """Test successful freeze note effect creation."""
    note_id = uuid4()
    effect = FreezeNoteEffect(note_id=note_id, duration=60)
    applied = effect.apply()

    assert applied.type == EffectType.FREEZE_NOTE
    payload = json.loads(applied.payload)
    assert payload["data"]["note_id"] == str(note_id)
    assert payload["data"]["duration"] == 60


def test_freeze_note_effect_default_duration() -> None:
    """Test freeze note effect with default duration."""
    note_id = uuid4()
    effect = FreezeNoteEffect(note_id=note_id)
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["duration"] == 300


def test_freeze_note_effect_invalid_duration() -> None:
    """Test freeze note effect with invalid duration raises validation error."""
    note_id = uuid4()
    with pytest.raises(ValidationError) as exc_info:
        FreezeNoteEffect(note_id=note_id, duration=0)

    errors = exc_info.value.errors()
    assert any("duration" in str(e["loc"]) for e in errors)


def test_freeze_note_effect_negative_duration() -> None:
    """Test freeze note effect with negative duration raises validation error."""
    note_id = uuid4()
    with pytest.raises(ValidationError) as exc_info:
        FreezeNoteEffect(note_id=note_id, duration=-1)

    errors = exc_info.value.errors()
    assert any("duration" in str(e["loc"]) for e in errors)


def test_freeze_note_effect_uuid_object() -> None:
    """Test freeze note effect accepts UUID object."""
    note_id = uuid4()
    effect = FreezeNoteEffect(note_id=note_id, duration=120)
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["note_id"] == str(note_id)


def test_freeze_note_effect_payload_structure() -> None:
    """Test freeze note effect payload has correct structure."""
    note_id = uuid4()
    effect = FreezeNoteEffect(note_id=note_id, duration=60)
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert "data" in payload
    assert "note_id" in payload["data"]
    assert "duration" in payload["data"]


def test_freeze_note_effect_with_user_id() -> None:
    """Test freeze note effect with user_id."""
    note_id = uuid4()
    user_id = "staff-key-123"
    effect = FreezeNoteEffect(note_id=note_id, duration=60, user_id=user_id)
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["user_id"] == user_id


def test_freeze_note_effect_without_user_id() -> None:
    """Test freeze note effect without user_id doesn't include it in payload."""
    note_id = uuid4()
    effect = FreezeNoteEffect(note_id=note_id, duration=60)
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert "user_id" not in payload["data"]


def test_unfreeze_note_effect_success() -> None:
    """Test successful unfreeze note effect creation."""
    note_id = uuid4()
    effect = UnfreezeNoteEffect(note_id=note_id)
    applied = effect.apply()

    assert applied.type == EffectType.UNFREEZE_NOTE
    payload = json.loads(applied.payload)
    assert payload["data"]["note_id"] == str(note_id)


def test_unfreeze_note_effect_uuid_object() -> None:
    """Test unfreeze note effect accepts UUID object."""
    note_id = uuid4()
    effect = UnfreezeNoteEffect(note_id=note_id)
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["note_id"] == str(note_id)


def test_unfreeze_note_effect_payload_structure() -> None:
    """Test unfreeze note effect payload has correct structure."""
    note_id = uuid4()
    effect = UnfreezeNoteEffect(note_id=note_id)
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert "data" in payload
    assert "note_id" in payload["data"]
    assert "duration" not in payload["data"]
