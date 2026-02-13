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
            ]
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
