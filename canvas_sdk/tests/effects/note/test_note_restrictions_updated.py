import json

import pytest

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.note.restrictions_updated import NoteRestrictionsUpdatedEffect


def test_effect_type() -> None:
    """NoteRestrictionsUpdatedEffect uses the NOTE_RESTRICTIONS_UPDATED effect type."""
    assert NoteRestrictionsUpdatedEffect.Meta.effect_type == EffectType.NOTE_RESTRICTIONS_UPDATED


def test_values() -> None:
    """values() returns the note_id."""
    effect = NoteRestrictionsUpdatedEffect(note_id="abc-123")
    assert effect.values == {"note_id": "abc-123"}


def test_apply_produces_correct_effect_type() -> None:
    """apply() returns an Effect with type NOTE_RESTRICTIONS_UPDATED."""
    applied = NoteRestrictionsUpdatedEffect(note_id="abc-123").apply()
    assert applied.type == EffectType.NOTE_RESTRICTIONS_UPDATED


def test_apply_payload_structure() -> None:
    """apply() wraps note_id under a 'data' key in the JSON payload."""
    applied = NoteRestrictionsUpdatedEffect(note_id="note-uuid-456").apply()
    payload = json.loads(applied.payload)
    assert payload == {"data": {"note_id": "note-uuid-456"}}


def test_note_id_is_required() -> None:
    """NoteRestrictionsUpdatedEffect raises when note_id is not provided."""
    from pydantic_core import ValidationError

    with pytest.raises(ValidationError):
        NoteRestrictionsUpdatedEffect()  # type: ignore[call-arg]


def test_note_id_accepts_uuid_string() -> None:
    """note_id accepts a standard UUID string."""
    uuid_str = "aaaaaaaa-0000-0000-0000-000000000001"
    effect = NoteRestrictionsUpdatedEffect(note_id=uuid_str)
    assert effect.note_id == uuid_str


def test_effect_payload_wraps_values_under_data_key() -> None:
    """effect_payload always wraps values under the 'data' key."""
    effect = NoteRestrictionsUpdatedEffect(note_id="note-123")
    assert effect.effect_payload == {"data": {"note_id": "note-123"}}


def test_patient_filter_defaults_to_none() -> None:
    """patient_filter inherited from _BaseEffect defaults to None."""
    assert NoteRestrictionsUpdatedEffect(note_id="note-123").patient_filter is None
