import json

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.note.note_restrictions import NoteRestrictionsEffect


def test_effect_type() -> None:
    """NoteRestrictionsEffect uses the NOTE_RESTRICTIONS effect type."""
    assert NoteRestrictionsEffect.Meta.effect_type == EffectType.NOTE_RESTRICTIONS


def test_defaults() -> None:
    """All fields default to their safe, unlocked values."""
    effect = NoteRestrictionsEffect()
    assert effect.restrict_access is False
    assert effect.blur_content is False
    assert effect.banner_message is None


def test_values_locked() -> None:
    """values() returns all three fields when the note is locked."""
    effect = NoteRestrictionsEffect(
        restrict_access=True,
        blur_content=True,
        banner_message="Locked for editing.",
    )
    assert effect.values == {
        "restrict_access": True,
        "blur_content": True,
        "banner_message": "Locked for editing.",
    }


def test_values_unlocked() -> None:
    """values() returns the correct payload when the note is not locked."""
    effect = NoteRestrictionsEffect()
    assert effect.values == {
        "restrict_access": False,
        "blur_content": False,
        "banner_message": None,
    }


def test_apply_produces_correct_effect_type() -> None:
    """apply() returns an Effect with type NOTE_RESTRICTIONS."""
    applied = NoteRestrictionsEffect(restrict_access=True).apply()
    assert applied.type == EffectType.NOTE_RESTRICTIONS


def test_apply_payload_structure() -> None:
    """apply() wraps values under a 'data' key in the JSON payload."""
    applied = NoteRestrictionsEffect(
        restrict_access=True,
        blur_content=False,
        banner_message="Please wait.",
    ).apply()

    payload = json.loads(applied.payload)
    assert "data" in payload
    data = payload["data"]
    assert data["restrict_access"] is True
    assert data["blur_content"] is False
    assert data["banner_message"] == "Please wait."


def test_apply_payload_without_message() -> None:
    """apply() includes banner_message as None when not set."""
    applied = NoteRestrictionsEffect(restrict_access=True).apply()
    data = json.loads(applied.payload)["data"]
    assert data["banner_message"] is None


def test_blur_without_restrict_access() -> None:
    """blur_content can be set independently of restrict_access."""
    effect = NoteRestrictionsEffect(restrict_access=False, blur_content=True)
    assert effect.values["blur_content"] is True
    assert effect.values["restrict_access"] is False


def test_effect_payload_wraps_values_under_data_key() -> None:
    """effect_payload always wraps values under the 'data' key."""
    effect = NoteRestrictionsEffect(restrict_access=True, banner_message="Locked.")
    assert effect.effect_payload == {"data": effect.values}


def test_patient_filter_defaults_to_none() -> None:
    """patient_filter inherited from _BaseEffect defaults to None."""
    assert NoteRestrictionsEffect().patient_filter is None


def test_patient_filter_can_be_set() -> None:
    """patient_filter can be configured for scoped restrictions."""
    effect = NoteRestrictionsEffect(patient_filter={"key": "patient-123"})
    assert effect.patient_filter == {"key": "patient-123"}


def test_all_fields_in_payload() -> None:
    """Every field is present in the applied payload regardless of value."""
    applied = NoteRestrictionsEffect(
        restrict_access=False, blur_content=False, banner_message=None
    ).apply()
    data = json.loads(applied.payload)["data"]
    assert set(data.keys()) == {"restrict_access", "blur_content", "banner_message"}
