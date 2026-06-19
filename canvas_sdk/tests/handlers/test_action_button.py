import json
from unittest.mock import MagicMock, patch

import pytest
from pytest import MonkeyPatch

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects import Effect
from canvas_sdk.effects.note import (
    ACTION_STATE_MATRIX,
    APPOINTMENT_TRANSITION_MATRIX,
    TRANSITION_STATE_MATRIX,
    transition_matrix_for,
)
from canvas_sdk.effects.show_button import ShowButtonEffect
from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.handlers.action_button import (
    SHOW_BUTTON_REGEX,
    ActionButton,
    NoteStateActionButton,
)
from canvas_sdk.v1.data.note import NoteStates, NoteTypeCategories


class ExampleActionButton(ActionButton):
    """A concrete implementation of ActionButton for testing."""

    BUTTON_TITLE = "Test Button"
    BUTTON_KEY = "test_button_key"
    BUTTON_LOCATION = ActionButton.ButtonLocation.NOTE_HEADER
    PRIORITY = 5
    BUTTON_TEXT_COLOR = "#FF0000"

    def handle(self) -> list[Effect]:
        """Handle button click by returning a mock effect."""
        return [ShowButtonEffect(key="result", title="Clicked", priority=0).apply()]


class InvisibleActionButton(ActionButton):
    """An action button that is never visible."""

    BUTTON_TITLE = "Hidden Button"
    BUTTON_KEY = "hidden_key"
    BUTTON_LOCATION = ActionButton.ButtonLocation.NOTE_FOOTER
    PRIORITY = 0

    def handle(self) -> list[Effect]:
        """Handle button click."""
        return []

    def visible(self) -> bool:
        """Always hidden."""
        return False


class NoColorActionButton(ActionButton):
    """An action button with no color."""

    BUTTON_TITLE = "No Color"
    BUTTON_KEY = "no_color_key"
    BUTTON_LOCATION = ActionButton.ButtonLocation.NOTE_BODY
    PRIORITY = 0

    def handle(self) -> list[Effect]:
        """Handle button click."""
        return []


# --- SHOW_BUTTON_REGEX tests ---


def test_show_button_regex_matches_show_events() -> None:
    """Test that SHOW_BUTTON_REGEX matches SHOW_*_BUTTON event names."""
    match = SHOW_BUTTON_REGEX.fullmatch("SHOW_NOTE_HEADER_BUTTON")
    assert match is not None, "Expected regex to match SHOW_NOTE_HEADER_BUTTON"
    assert match.group(1) == "NOTE_HEADER", "Expected extracted location to be NOTE_HEADER"


def test_show_button_regex_extracts_location() -> None:
    """Test that the regex extracts location correctly for various events."""
    cases = {
        "SHOW_NOTE_FOOTER_BUTTON": "NOTE_FOOTER",
        "SHOW_NOTE_BODY_BUTTON": "NOTE_BODY",
        "SHOW_CHART_PATIENT_HEADER_BUTTON": "CHART_PATIENT_HEADER",
        "SHOW_CHART_SUMMARY_GOALS_SECTION_BUTTON": "CHART_SUMMARY_GOALS_SECTION",
    }
    for event_name, expected_location in cases.items():
        match = SHOW_BUTTON_REGEX.fullmatch(event_name)
        assert match is not None, f"Expected regex to match {event_name}"
        assert match.group(1) == expected_location


def test_show_button_regex_does_not_match_non_show_events() -> None:
    """Test that the regex does not match non-SHOW events."""
    assert SHOW_BUTTON_REGEX.fullmatch("ACTION_BUTTON_CLICKED") is None
    assert SHOW_BUTTON_REGEX.fullmatch("SHOW_BUTTON") is None
    assert SHOW_BUTTON_REGEX.fullmatch("RANDOM_EVENT") is None


# --- RESPONDS_TO tests ---


def test_responds_to_contains_expected_event_types() -> None:
    """Test that RESPONDS_TO includes all show button events and ACTION_BUTTON_CLICKED."""
    assert "ACTION_BUTTON_CLICKED" in ActionButton.RESPONDS_TO
    assert "SHOW_NOTE_HEADER_BUTTON" in ActionButton.RESPONDS_TO
    assert "SHOW_NOTE_FOOTER_BUTTON" in ActionButton.RESPONDS_TO
    assert "SHOW_NOTE_BODY_BUTTON" in ActionButton.RESPONDS_TO
    assert "SHOW_CHART_PATIENT_HEADER_BUTTON" in ActionButton.RESPONDS_TO


# --- ButtonLocation enum tests ---


def test_button_location_enum_values() -> None:
    """Test that ButtonLocation enum has expected values."""
    assert ActionButton.ButtonLocation.NOTE_HEADER.value == "note_header"
    assert ActionButton.ButtonLocation.NOTE_FOOTER.value == "note_footer"
    assert ActionButton.ButtonLocation.NOTE_BODY.value == "note_body"
    assert ActionButton.ButtonLocation.CHART_PATIENT_HEADER.value == "chart_patient_header"


# --- visible() tests ---


def test_default_visible_returns_true() -> None:
    """Test that the default visible() method returns True."""
    event = Event(EventRequest(type=EventType.SHOW_NOTE_HEADER_BUTTON))
    button = ExampleActionButton(event)
    assert button.visible() is True, "Default visible() should return True"


# --- compute() show event tests ---


def test_compute_show_event_matching_location() -> None:
    """Test compute returns ShowButtonEffect for matching show event and location."""
    event = Event(EventRequest(type=EventType.SHOW_NOTE_HEADER_BUTTON))
    button = ExampleActionButton(event)
    result = button.compute()

    assert len(result) == 1, "Expected a single effect for matching location"
    assert isinstance(result[0], Effect), "Effect should be an instance of Effect"


def test_compute_show_event_non_matching_location() -> None:
    """Test compute returns empty list when show event location doesn't match."""
    event = Event(EventRequest(type=EventType.SHOW_NOTE_FOOTER_BUTTON))
    button = ExampleActionButton(event)
    result = button.compute()

    assert result == [], "Expected no effects when location doesn't match"


def test_compute_show_event_invisible_button() -> None:
    """Test compute returns empty list when button is not visible."""
    event = Event(EventRequest(type=EventType.SHOW_NOTE_FOOTER_BUTTON))
    button = InvisibleActionButton(event)
    result = button.compute()

    assert result == [], "Expected no effects when button is not visible"


def test_compute_show_button_effect_properties() -> None:
    """Test that the ShowButtonEffect has correct properties from the handler."""
    event = Event(EventRequest(type=EventType.SHOW_NOTE_HEADER_BUTTON))
    button = ExampleActionButton(event)
    effects = button.compute()

    assert len(effects) == 1
    payload = json.loads(effects[0].payload)
    assert payload["data"]["key"] == "test_button_key"
    assert payload["data"]["title"] == "Test Button"
    assert payload["data"]["priority"] == 5
    assert payload["data"]["color"] == "#FF0000"


def test_compute_show_button_effect_no_color() -> None:
    """Test that ShowButtonEffect works when COLOR is None."""
    event = Event(EventRequest(type=EventType.SHOW_NOTE_BODY_BUTTON))
    button = NoColorActionButton(event)
    effects = button.compute()

    assert len(effects) == 1
    payload = json.loads(effects[0].payload)
    assert payload["data"]["color"] is None


# --- compute() no location tests ---


def test_compute_no_button_location() -> None:
    """Test compute returns empty list when BUTTON_LOCATION is falsy."""

    class NoLocationButton(ActionButton):
        BUTTON_TITLE = "No Location"
        BUTTON_KEY = "no_loc"
        BUTTON_LOCATION = ""  # type: ignore[assignment]
        PRIORITY = 0

        def handle(self) -> list[Effect]:
            return []

    event = Event(EventRequest(type=EventType.SHOW_NOTE_HEADER_BUTTON))
    button = NoLocationButton(event)
    assert button.compute() == [], "Expected no effects when BUTTON_LOCATION is falsy"


# --- NoteStateActionButton tests ---


class _LockButton(NoteStateActionButton):
    STATE_ACTION = NoteStates.LOCKED


class _SignButton(NoteStateActionButton):
    STATE_ACTION = NoteStates.SIGNED


class _DeleteButton(NoteStateActionButton):
    STATE_ACTION = NoteStates.DELETED


class _UndeleteButton(NoteStateActionButton):
    STATE_ACTION = NoteStates.UNDELETED


class _CheckInButton(NoteStateActionButton):
    STATE_ACTION = NoteStates.CONVERTED


class _NoShowButton(NoteStateActionButton):
    STATE_ACTION = NoteStates.NOSHOW


class _DischargeButton(NoteStateActionButton):
    STATE_ACTION = NoteStates.DISCHARGED


class _CancelButton(NoteStateActionButton):
    STATE_ACTION = NoteStates.CANCELLED


class _RestoreAppointmentButton(NoteStateActionButton):
    STATE_ACTION = NoteStates.REVERTED


def _make_state_handler(
    cls: type[NoteStateActionButton], monkeypatch: MonkeyPatch, note_id: int | None
) -> NoteStateActionButton:
    """Instantiate a NoteStateActionButton with a context exposing the given note_id."""
    handler = cls(event=MagicMock())
    monkeypatch.setattr(type(handler), "context", property(lambda self: {"note_id": note_id}))
    return handler


def _fake_note(
    state: str,
    is_sig_required: bool = True,
    category: str = NoteTypeCategories.ENCOUNTER,
) -> MagicMock:
    """A note stand-in whose current_state and note_type_version satisfy the validators."""
    note = MagicMock()
    note.id = "11111111-1111-1111-1111-111111111111"
    note.current_state = MagicMock(state=state)
    note.note_type_version = MagicMock(
        is_sig_required=is_sig_required, is_billable=True, category=category
    )
    return note


def test_note_state_button_derives_title_and_key() -> None:
    """Title and key are derived from STATE_ACTION when not set explicitly."""
    assert _LockButton.BUTTON_TITLE == "Lock"
    assert _LockButton.BUTTON_KEY == "note_state_action__LKD"
    assert _SignButton.BUTTON_TITLE == "Sign"


def test_note_state_button_is_footer_button_and_clickable() -> None:
    """Note-state buttons live in the footer and respond to clicks."""
    assert _LockButton.BUTTON_LOCATION == ActionButton.ButtonLocation.NOTE_FOOTER
    assert "ACTION_BUTTON_CLICKED" in NoteStateActionButton.RESPONDS_TO


@pytest.mark.parametrize(
    ("button", "state", "is_sig_required", "expected"),
    [
        # Lock and Sign are the same transition, split by is_sig_required.
        (_LockButton, NoteStates.NEW, False, True),  # non-sig note shows Lock
        (_LockButton, NoteStates.NEW, True, False),  # sig note shows Sign, not Lock
        (_LockButton, NoteStates.LOCKED, False, False),  # LOCKED -> [UNLOCKED] only
        (_SignButton, NoteStates.NEW, True, True),  # sig note shows Sign
        (_SignButton, NoteStates.NEW, False, False),  # non-sig note shows Lock, not Sign
        (_SignButton, NoteStates.LOCKED, True, False),  # LOCKED -> [UNLOCKED] only
    ],
)
def test_note_state_button_visibility_follows_matrix(
    button: type[NoteStateActionButton],
    state: str,
    is_sig_required: bool,
    expected: bool,
    monkeypatch: MonkeyPatch,
) -> None:
    """A button is visible iff its target state is reachable and the sig gate allows it."""
    handler = _make_state_handler(button, monkeypatch, note_id=5)
    with patch("canvas_sdk.handlers.action_button.Note.objects") as mock_note:
        mock_note.filter.return_value.first.return_value = _fake_note(state, is_sig_required)
        assert handler.visible() is expected


def test_note_state_button_not_visible_without_note(monkeypatch: MonkeyPatch) -> None:
    """No note in context -> not visible."""
    handler = _make_state_handler(_LockButton, monkeypatch, note_id=None)
    assert handler.visible() is False


def test_note_state_button_handle_returns_transition_and_reload(
    monkeypatch: MonkeyPatch,
) -> None:
    """A click applies the transition AND reloads the footer."""
    handler = _make_state_handler(_LockButton, monkeypatch, note_id=5)
    fake_note = _fake_note(NoteStates.NEW)
    with (
        patch("canvas_sdk.v1.data.PracticeLocation.objects"),
        patch("canvas_sdk.v1.data.Staff.objects"),
        patch("canvas_sdk.v1.data.Patient.objects"),
        patch("canvas_sdk.v1.data.Note.objects") as mock_note,
    ):
        mock_note.filter.return_value.first.return_value = fake_note
        effects = handler.handle()

    assert len(effects) == 2
    assert effects[0].type == EffectType.LOCK_NOTE
    assert effects[1].type == EffectType.RELOAD_ACTION_BUTTONS


def test_sign_button_handle_locks_then_signs(monkeypatch: MonkeyPatch) -> None:
    """A note can only be signed once locked, so signing emits lock, then sign, then reload."""
    handler = _make_state_handler(_SignButton, monkeypatch, note_id=5)
    fake_note = _fake_note(NoteStates.NEW)  # is_sig_required by default
    with (
        patch("canvas_sdk.v1.data.PracticeLocation.objects"),
        patch("canvas_sdk.v1.data.Staff.objects"),
        patch("canvas_sdk.v1.data.Patient.objects"),
        patch("canvas_sdk.v1.data.Note.objects") as mock_note,
    ):
        mock_note.filter.return_value.first.return_value = fake_note
        effects = handler.handle()

    assert [effect.type for effect in effects] == [
        EffectType.LOCK_NOTE,
        EffectType.SIGN_NOTE,
        EffectType.RELOAD_ACTION_BUTTONS,
    ]


@pytest.mark.parametrize(
    ("button", "action_method"),
    [
        (_CancelButton, "cancel"),
        (_RestoreAppointmentButton, "revert"),
    ],
)
def test_appointment_button_handle_acts_on_the_appointment(
    button: type[NoteStateActionButton],
    action_method: str,
    monkeypatch: MonkeyPatch,
) -> None:
    """Cancel/Restore resolve the note's appointment id and emit its Appointment effect."""
    handler = _make_state_handler(button, monkeypatch, note_id=5)
    sentinel = MagicMock(spec=Effect)
    with (
        patch("canvas_sdk.handlers.action_button.Note.objects") as mock_note,
        patch("canvas_sdk.handlers.action_button.AppointmentModel.objects") as mock_appt,
        patch("canvas_sdk.handlers.action_button.AppointmentEffect") as mock_effect_cls,
    ):
        mock_note.filter.return_value.values_list.return_value.first.return_value = "note-ext-id"
        mock_appt.filter.return_value.values_list.return_value.first.return_value = "appt-id"
        getattr(mock_effect_cls.return_value, action_method).return_value = sentinel
        effects = handler.handle()

    mock_effect_cls.assert_called_once_with(instance_id="appt-id")
    getattr(mock_effect_cls.return_value, action_method).assert_called_once_with()
    assert effects[0] is sentinel
    assert effects[1].type == EffectType.RELOAD_ACTION_BUTTONS


@pytest.mark.parametrize(
    ("button", "state", "category", "expected"),
    [
        (_DeleteButton, NoteStates.NEW, NoteTypeCategories.ENCOUNTER, True),  # NEW allows Delete
        (_DeleteButton, NoteStates.LOCKED, NoteTypeCategories.ENCOUNTER, False),  # LOCKED does not
        (_UndeleteButton, NoteStates.DELETED, NoteTypeCategories.ENCOUNTER, True),  # -> Restore
        (_DischargeButton, NoteStates.NEW, NoteTypeCategories.ENCOUNTER, True),  # NEW allows it
        (_DischargeButton, NoteStates.LOCKED, NoteTypeCategories.ENCOUNTER, False),
        (_CheckInButton, NoteStates.BOOKED, NoteTypeCategories.APPOINTMENT, True),  # check-in
        (_CheckInButton, NoteStates.NEW, NoteTypeCategories.ENCOUNTER, False),
        (_NoShowButton, NoteStates.BOOKED, NoteTypeCategories.APPOINTMENT, True),  # no-show
        (_NoShowButton, NoteStates.NOSHOW, NoteTypeCategories.APPOINTMENT, False),
    ],
)
def test_note_state_button_visibility_covers_all_sdk_actions(
    button: type[NoteStateActionButton],
    state: str,
    category: str,
    expected: bool,
    monkeypatch: MonkeyPatch,
) -> None:
    """The newly-reachable actions (delete/undelete/discharge/check-in/no-show) gate correctly."""
    handler = _make_state_handler(button, monkeypatch, note_id=5)
    with patch("canvas_sdk.handlers.action_button.Note.objects") as mock_note:
        mock_note.filter.return_value.first.return_value = _fake_note(state, category=category)
        assert handler.visible() is expected


def test_every_sdk_action_target_state_is_reachable() -> None:
    """Every transition the SDK can perform has a reachable target across both matrices."""
    reachable = {
        state
        for matrix in (TRANSITION_STATE_MATRIX, APPOINTMENT_TRANSITION_MATRIX)
        for targets in matrix.values()
        for state in targets
    }
    assert set(ACTION_STATE_MATRIX.values()) <= reachable


@pytest.mark.parametrize(
    ("button", "state", "expected"),
    [
        # Appointment notes use the appointment matrix, not the encounter one.
        (_CheckInButton, NoteStates.BOOKED, True),  # BOOKED -> check in / no show
        (_NoShowButton, NoteStates.BOOKED, True),
        (_CancelButton, NoteStates.BOOKED, True),  # a booked appointment can be cancelled
        (_RestoreAppointmentButton, NoteStates.CANCELLED, True),  # cancelled -> restore
        (_CancelButton, NoteStates.LOCKED, False),  # locked appointment only unlocks
        (_LockButton, NoteStates.NOSHOW, True),  # a no-showed appointment can be locked
        (_LockButton, NoteStates.NEW, False),  # NEW isn't part of the appointment flow
        (_SignButton, NoteStates.NOSHOW, False),  # appointments are never signed
    ],
)
def test_appointment_notes_use_appointment_matrix(
    button: type[NoteStateActionButton],
    state: str,
    expected: bool,
    monkeypatch: MonkeyPatch,
) -> None:
    """Appointment-category notes gate their buttons off APPOINTMENT_TRANSITION_MATRIX."""
    handler = _make_state_handler(button, monkeypatch, note_id=5)
    with patch("canvas_sdk.handlers.action_button.Note.objects") as mock_note:
        mock_note.filter.return_value.first.return_value = _fake_note(
            state, is_sig_required=False, category=NoteTypeCategories.APPOINTMENT
        )
        assert handler.visible() is expected


def test_transition_matrix_for_selects_by_category() -> None:
    """transition_matrix_for returns the appointment matrix only for appointment notes."""
    assert transition_matrix_for(NoteTypeCategories.APPOINTMENT) is APPOINTMENT_TRANSITION_MATRIX
    assert transition_matrix_for(NoteTypeCategories.ENCOUNTER) is TRANSITION_STATE_MATRIX
    assert transition_matrix_for(None) is TRANSITION_STATE_MATRIX
