import json
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from pydantic_core import InitErrorDetails, PydanticCustomError, ValidationError
from pytest import MonkeyPatch

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.v1.data.note import NoteStates, NoteTypeCategories
from note_state_transition_buttons.handlers.transition_buttons import (
    CancelAppointmentButton,
    CheckInNoteButton,
    DeleteNoteButton,
    DischargeNoteButton,
    LockNoteButton,
    LOG_SCHEMA_KEY,
    NoShowNoteButton,
    PushChargesNoteButton,
    RevertAppointmentButton,
    SignNoteButton,
    UndeleteNoteButton,
    UnlockNoteButton,
    _TransitionButton,
)


ALL_BUTTONS = [
    LockNoteButton,
    UnlockNoteButton,
    SignNoteButton,
    PushChargesNoteButton,
    CheckInNoteButton,
    NoShowNoteButton,
    DeleteNoteButton,
    UndeleteNoteButton,
    DischargeNoteButton,
    CancelAppointmentButton,
    RevertAppointmentButton,
]


def _validation_error(message: str) -> ValidationError:
    return ValidationError.from_exception_data(
        "Note",
        [
            InitErrorDetails(
                type=PydanticCustomError("value_error", message),
                loc=("instance_id",),
                input=None,
            )
        ],
    )


def _make_handler(cls: type[_TransitionButton], monkeypatch: MonkeyPatch, note_uuid: str | None):
    handler = cls(event=MagicMock())
    monkeypatch.setattr(type(handler), "context", property(lambda self: {"note_id": note_uuid}))
    return handler


# Buttons whose SDK call passes validation only when the underlying note's
# `note_type_version.category` matches a specific value. Buttons not in this
# map accept the default INPATIENT category.
_REQUIRED_CATEGORY: dict[str, NoteTypeCategories] = {
    "NSTL_CHECK_IN": NoteTypeCategories.APPOINTMENT,
    "NSTL_NO_SHOW": NoteTypeCategories.APPOINTMENT,
}


@pytest.fixture
def mock_sdk_db_queries(request: pytest.FixtureRequest) -> Generator[None]:
    """Stub out the DB calls that `Note(...).method()` validators make so the
    parametrized test can run without a real Django DB. Pick the note category
    based on the button under test so the transition matrix passes."""
    button_key = getattr(request, "param", None)
    category = _REQUIRED_CATEGORY.get(button_key, NoteTypeCategories.INPATIENT)
    fake_note = MagicMock()
    fake_note.current_state = MagicMock(state=NoteStates.LOCKED)
    fake_note.note_type_version = MagicMock(
        is_sig_required=True,
        is_billable=True,
        category=category,
    )
    with (
        patch("canvas_sdk.v1.data.PracticeLocation.objects") as mock_pl,
        patch("canvas_sdk.v1.data.Staff.objects") as mock_staff,
        patch("canvas_sdk.v1.data.Patient.objects") as mock_patient,
        patch("canvas_sdk.v1.data.Note.objects") as mock_note,
        patch("canvas_sdk.v1.data.appointment.Appointment.objects") as mock_appt,
    ):
        for mock in (mock_pl, mock_staff, mock_patient, mock_note, mock_appt):
            mock.filter.return_value.exists.return_value = True
        mock_note.filter.return_value.first.return_value = fake_note
        yield


def test_every_button_is_a_note_footer_button() -> None:
    """Every transition button lives in the note footer with a unique key."""
    keys = [cls.BUTTON_KEY for cls in ALL_BUTTONS]
    assert len(set(keys)) == len(keys), "BUTTON_KEY must be unique per button"
    for cls in ALL_BUTTONS:
        assert cls.BUTTON_LOCATION == _TransitionButton.ButtonLocation.NOTE_FOOTER


def test_handle_returns_empty_when_no_note_id(monkeypatch: MonkeyPatch) -> None:
    handler = _make_handler(LockNoteButton, monkeypatch, note_uuid=None)
    assert handler.handle() == []


def test_handle_logs_validation_error_when_sdk_rejects(monkeypatch: MonkeyPatch) -> None:
    """A discharge call against an encounter note raises ValidationError before
    the transition effect is emitted; the handler should emit a single log
    command containing the error text."""
    note_uuid = "11111111-1111-1111-1111-111111111111"
    handler = _make_handler(DischargeNoteButton, monkeypatch, note_uuid=note_uuid)

    def _raise(self, note_uuid: str):
        raise _validation_error("discharge rejected")

    monkeypatch.setattr(DischargeNoteButton, "_build_transition_effect", _raise)

    effects = handler.handle()

    assert len(effects) == 1
    log = effects[0]
    payload = json.loads(log.payload)
    assert payload["data"]["schema_key"] == LOG_SCHEMA_KEY
    assert "Discharge failed validation" in payload["data"]["content"]
    assert payload["note"] == note_uuid


def test_handle_emits_transition_plus_success_log(monkeypatch: MonkeyPatch) -> None:
    """A valid transition is emitted alongside a success log command."""
    note_uuid = "22222222-2222-2222-2222-222222222222"
    handler = _make_handler(LockNoteButton, monkeypatch, note_uuid=note_uuid)

    sentinel = MagicMock(name="lock_effect")

    def _ok(self, note_uuid: str):
        return sentinel

    monkeypatch.setattr(LockNoteButton, "_build_transition_effect", _ok)

    effects = handler.handle()

    assert effects[0] is sentinel
    log_payload = json.loads(effects[1].payload)
    assert log_payload["data"]["schema_key"] == LOG_SCHEMA_KEY
    assert log_payload["data"]["content"] == "Lock transition applied."
    assert log_payload["note"] == note_uuid


@pytest.mark.parametrize(
    "button_cls,expected_effect,mock_sdk_db_queries",
    [
        (LockNoteButton, EffectType.LOCK_NOTE, LockNoteButton.BUTTON_KEY),
        (UnlockNoteButton, EffectType.UNLOCK_NOTE, UnlockNoteButton.BUTTON_KEY),
        (SignNoteButton, EffectType.SIGN_NOTE, SignNoteButton.BUTTON_KEY),
        (PushChargesNoteButton, EffectType.PUSH_NOTE_CHARGES, PushChargesNoteButton.BUTTON_KEY),
        (CheckInNoteButton, EffectType.CHECK_IN_NOTE, CheckInNoteButton.BUTTON_KEY),
        (NoShowNoteButton, EffectType.NO_SHOW_NOTE, NoShowNoteButton.BUTTON_KEY),
        (DeleteNoteButton, EffectType.DELETE_NOTE, DeleteNoteButton.BUTTON_KEY),
        (UndeleteNoteButton, EffectType.UNDELETE_NOTE, UndeleteNoteButton.BUTTON_KEY),
        (DischargeNoteButton, EffectType.DISCHARGE_NOTE, DischargeNoteButton.BUTTON_KEY),
        (CancelAppointmentButton, EffectType.CANCEL_APPOINTMENT, CancelAppointmentButton.BUTTON_KEY),
        (RevertAppointmentButton, EffectType.REVERT_APPOINTMENT, RevertAppointmentButton.BUTTON_KEY),
    ],
    indirect=["mock_sdk_db_queries"],
)
def test_each_button_targets_its_effect_type(
    button_cls: type[_TransitionButton],
    expected_effect: int,
    monkeypatch: MonkeyPatch,
    mock_sdk_db_queries: None,
) -> None:
    """Each button's `_build_transition_effect` returns the matching SDK effect."""
    note_uuid = "33333333-3333-3333-3333-333333333333"
    handler = _make_handler(button_cls, monkeypatch, note_uuid=note_uuid)
    effect = handler._build_transition_effect(note_uuid)
    assert effect.type == expected_effect
