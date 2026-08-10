import json
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

import pytest
from django.core.exceptions import ValidationError
from pydantic_core._pydantic_core import ValidationError as PydanticValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.patient.timeline import PatientTimelineEffect


def test_effect_type_is_patient_timeline_configuration() -> None:
    """Test that the effect type is correctly set."""
    assert PatientTimelineEffect.Meta.effect_type == EffectType.PATIENT_TIMELINE__CONFIGURATION


@patch("canvas_sdk.effects.patient.timeline.NoteType.objects.filter")
def test_apply_returns_correct_effect(mock_filter: MagicMock) -> None:
    """Test that apply() returns an Effect with correct type and payload."""
    uuid1 = UUID("12345678-1234-5678-1234-567812345678")
    uuid2 = UUID("87654321-4321-8765-4321-876543218765")
    mock_filter.return_value.values_list.return_value = [str(uuid1), str(uuid2)]
    effect = PatientTimelineEffect(excluded_note_types=[uuid1, uuid2])

    applied = effect.apply()
    payload = json.loads(applied.payload)

    assert applied.type == EffectType.PATIENT_TIMELINE__CONFIGURATION
    assert payload == {
        "data": {
            "excluded_note_types": [
                "12345678-1234-5678-1234-567812345678",
                "87654321-4321-8765-4321-876543218765",
            ],
            # Not supplied, so no constraint on the New Note button.
            "allowed_new_note_types": None,
        }
    }


def test_invalid_string_raises_validation_error() -> None:
    """Test that non-UUID strings raise a ValidationError."""
    with pytest.raises(ValidationError):
        PatientTimelineEffect(excluded_note_types=["invalid-not-a-uuid"]).apply()


@patch("canvas_sdk.effects.patient.timeline.NoteType.objects.filter")
def test_get_error_details_valid_note_types(mock_filter: MagicMock) -> None:
    """Test that no errors are returned when all note types exist."""
    uuid1 = str(uuid4())
    uuid2 = str(uuid4())
    mock_filter.return_value.values_list.return_value = [uuid1, uuid2]
    effect = PatientTimelineEffect(excluded_note_types=[uuid1, uuid2])

    errors = effect._get_error_details(method=None)

    assert errors == []


@patch("canvas_sdk.effects.patient.timeline.NoteType.objects.filter")
def test_get_error_details_invalid_note_type(mock_filter: MagicMock) -> None:
    """Test that an error is returned when a note type does not exist."""
    nonexistent_uuid = str(uuid4())
    mock_filter.return_value.values_list.return_value = []
    effect = PatientTimelineEffect(excluded_note_types=[nonexistent_uuid])

    with pytest.raises(PydanticValidationError) as exc_info:
        effect.apply()

    errors = exc_info.value.errors()
    assert any(f"Note type '{nonexistent_uuid}' not found" in str(e) for e in errors)


@patch("canvas_sdk.effects.patient.timeline.NoteType.objects.filter")
def test_get_error_details_empty_list_no_errors(mock_filter: MagicMock) -> None:
    """Test that no errors are returned when excluded_note_types is empty."""
    effect = PatientTimelineEffect(excluded_note_types=[])

    errors = effect._get_error_details(method=None)

    assert errors == []
    mock_filter.assert_not_called()


def test_excluded_note_types_is_optional() -> None:
    """Test that a plugin restricting only the New Note button need not pass exclusions."""
    payload = json.loads(PatientTimelineEffect().apply().payload)

    assert payload == {
        "data": {"excluded_note_types": [], "allowed_new_note_types": None},
    }


@patch("canvas_sdk.effects.patient.timeline.NoteType.objects.filter")
def test_allowed_new_note_types_is_serialized(mock_filter: MagicMock) -> None:
    """Test that the New Note allow-list round-trips into the payload."""
    note_type_id = str(uuid4())
    mock_filter.return_value.values_list.return_value = [note_type_id]

    payload = json.loads(
        PatientTimelineEffect(allowed_new_note_types=[note_type_id]).apply().payload
    )

    assert payload["data"]["allowed_new_note_types"] == [note_type_id]
    assert payload["data"]["excluded_note_types"] == []


def test_empty_allow_list_is_distinct_from_none() -> None:
    """Test that [] and None serialize differently.

    home-app reads None as "no constraint" and [] as "offer no note types", which hides the
    New Note button, so the two must not collapse onto each other.
    """
    unset = json.loads(PatientTimelineEffect().apply().payload)
    empty = json.loads(PatientTimelineEffect(allowed_new_note_types=[]).apply().payload)

    assert unset["data"]["allowed_new_note_types"] is None
    assert empty["data"]["allowed_new_note_types"] == []


@patch("canvas_sdk.effects.patient.timeline.NoteType.objects.filter")
def test_both_fields_can_be_set_together(mock_filter: MagicMock) -> None:
    """Test that a plugin can hide history and restrict creation in one effect."""
    excluded = str(uuid4())
    allowed = str(uuid4())
    mock_filter.return_value.values_list.return_value = [excluded, allowed]

    payload = json.loads(
        PatientTimelineEffect(excluded_note_types=[excluded], allowed_new_note_types=[allowed])
        .apply()
        .payload
    )

    assert payload["data"]["excluded_note_types"] == [excluded]
    assert payload["data"]["allowed_new_note_types"] == [allowed]


@patch("canvas_sdk.effects.patient.timeline.NoteType.objects.filter")
def test_unknown_note_type_in_the_allow_list_raises(mock_filter: MagicMock) -> None:
    """Test that the allow-list is validated too, not just the exclusion list."""
    nonexistent = str(uuid4())
    mock_filter.return_value.values_list.return_value = []

    with pytest.raises(PydanticValidationError) as exc_info:
        PatientTimelineEffect(allowed_new_note_types=[nonexistent]).apply()

    assert any(f"Note type '{nonexistent}' not found" in str(e) for e in exc_info.value.errors())


@patch("canvas_sdk.effects.patient.timeline.NoteType.objects.filter")
def test_both_lists_are_validated_in_a_single_query(mock_filter: MagicMock) -> None:
    """Test that validating both fields costs one query over the union of the two."""
    excluded = str(uuid4())
    allowed = str(uuid4())
    mock_filter.return_value.values_list.return_value = [excluded, allowed]

    PatientTimelineEffect(excluded_note_types=[excluded], allowed_new_note_types=[allowed]).apply()

    mock_filter.assert_called_once()
    assert set(mock_filter.call_args.kwargs["unique_identifier__in"]) == {excluded, allowed}
