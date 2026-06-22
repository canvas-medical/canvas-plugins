"""Tests for the note/patient action-button reload effects."""

import json
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.action_button import (
    ReloadNoteActionButtonsEffect,
    ReloadPatientActionButtonsEffect,
)

NOTE_OBJECTS = "canvas_sdk.effects.action_button.Note.objects"
PATIENT_OBJECTS = "canvas_sdk.effects.action_button.Patient.objects"


def test_reload_note_payload() -> None:
    """A note reload carries the note id when the note exists."""
    with patch(NOTE_OBJECTS) as note_objects:
        note_objects.filter.return_value.exists.return_value = True
        effect = ReloadNoteActionButtonsEffect(id="42").apply()

    assert isinstance(effect, Effect)
    assert effect.type == EffectType.RELOAD_ACTION_BUTTONS
    data = json.loads(effect.payload)["data"]
    assert data == {"note_id": "42", "patient_id": None}


def test_reload_note_requires_id() -> None:
    """A note reload without an id is rejected at construction."""
    with pytest.raises(ValidationError):
        ReloadNoteActionButtonsEffect()  # type: ignore[call-arg]


def test_reload_note_rejects_missing_note() -> None:
    """A note reload for a note that does not exist is rejected at apply time."""
    with patch(NOTE_OBJECTS) as note_objects:
        note_objects.filter.return_value.exists.return_value = False
        with pytest.raises(ValidationError):
            ReloadNoteActionButtonsEffect(id="404").apply()


def test_reload_patient_payload() -> None:
    """A patient reload carries the patient id when it exists."""
    with patch(PATIENT_OBJECTS) as patient_objects:
        patient_objects.filter.return_value.exists.return_value = True
        effect = ReloadPatientActionButtonsEffect(id="patient-1").apply()

    assert effect.type == EffectType.RELOAD_ACTION_BUTTONS
    data = json.loads(effect.payload)["data"]
    assert data == {"note_id": None, "patient_id": "patient-1"}


def test_reload_patient_requires_id() -> None:
    """A patient reload without an id is rejected at construction."""
    with pytest.raises(ValidationError):
        ReloadPatientActionButtonsEffect()  # type: ignore[call-arg]


def test_reload_patient_rejects_missing_patient() -> None:
    """A patient reload for a patient that does not exist is rejected at apply time."""
    with patch(PATIENT_OBJECTS) as patient_objects:
        patient_objects.filter.return_value.exists.return_value = False
        with pytest.raises(ValidationError):
            ReloadPatientActionButtonsEffect(id="404").apply()
