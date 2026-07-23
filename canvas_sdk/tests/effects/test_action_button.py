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

# The note id is a UUID (accepted as a string via strict=False). The patient id is an opaque
# string — a dash-less UUID — passed through verbatim, so it is never re-serialized with dashes.
NOTE_ID = "11111111-1111-1111-1111-111111111111"
PATIENT_ID = "22222222222222222222222222222222"


def test_reload_note_payload() -> None:
    """A note reload carries the note id when the note exists."""
    with patch(NOTE_OBJECTS) as note_objects:
        note_objects.filter.return_value.exists.return_value = True
        effect = ReloadNoteActionButtonsEffect(id=NOTE_ID).apply()  # type: ignore[arg-type]

    assert isinstance(effect, Effect)
    assert effect.type == EffectType.RELOAD_ACTION_BUTTONS
    data = json.loads(effect.payload)["data"]
    assert data == {"note_id": NOTE_ID, "patient_id": None}


def test_reload_note_requires_id() -> None:
    """A note reload without an id is rejected at construction."""
    with pytest.raises(ValidationError):
        ReloadNoteActionButtonsEffect()  # type: ignore[call-arg]


def test_reload_note_rejects_missing_note() -> None:
    """A note reload for a note that does not exist is rejected at apply time."""
    with patch(NOTE_OBJECTS) as note_objects:
        note_objects.filter.return_value.exists.return_value = False
        with pytest.raises(ValidationError):
            ReloadNoteActionButtonsEffect(id=NOTE_ID).apply()  # type: ignore[arg-type]


def test_reload_patient_payload() -> None:
    """A patient reload carries the patient id when it exists."""
    with patch(PATIENT_OBJECTS) as patient_objects:
        patient_objects.filter.return_value.exists.return_value = True
        effect = ReloadPatientActionButtonsEffect(id=PATIENT_ID).apply()

    assert effect.type == EffectType.RELOAD_ACTION_BUTTONS
    data = json.loads(effect.payload)["data"]
    # The dash-less id is preserved verbatim (not re-serialized to canonical UUID form).
    assert data == {"note_id": None, "patient_id": PATIENT_ID}


def test_reload_patient_requires_id() -> None:
    """A patient reload without an id is rejected at construction."""
    with pytest.raises(ValidationError):
        ReloadPatientActionButtonsEffect()  # type: ignore[call-arg]


def test_reload_patient_rejects_missing_patient() -> None:
    """A patient reload for a patient that does not exist is rejected at apply time."""
    with patch(PATIENT_OBJECTS) as patient_objects:
        patient_objects.filter.return_value.exists.return_value = False
        with pytest.raises(ValidationError):
            ReloadPatientActionButtonsEffect(id=PATIENT_ID).apply()
