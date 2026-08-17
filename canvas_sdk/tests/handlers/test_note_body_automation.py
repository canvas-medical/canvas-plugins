import json
from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ImproperlyConfigured
from pydantic import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects import Effect
from canvas_sdk.effects.note_body_automation import ShowNoteBodyAutomationEffect
from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.handlers.note_body_automation import (
    AUTOMATION_SELECTED_EVENT,
    SHOW_AUTOMATIONS_EVENT,
    NoteBodyAutomation,
)

_HANDLE_EFFECT = ShowNoteBodyAutomationEffect(key="handled", title="Handled").apply()


class ExampleAutomation(NoteBodyAutomation):
    """A concrete NoteBodyAutomation for testing."""

    AUTOMATION_KEY = "test_automation"
    AUTOMATION_TITLE = "Test Automation"
    KEYWORDS = ["test", "example"]
    PRIORITY = 5

    def handle(self) -> list[Effect]:
        """Return one effect, so the test can tell the selection ran."""
        return [_HANDLE_EFFECT]


class InvisibleAutomation(NoteBodyAutomation):
    """A NoteBodyAutomation that never shows."""

    AUTOMATION_KEY = "hidden_automation"
    AUTOMATION_TITLE = "Hidden Automation"

    def handle(self) -> list[Effect]:
        """Return no effects."""
        return []

    def visible(self) -> bool:
        """Never show."""
        return False


def _show_event() -> Event:
    """Build the event Canvas fires to collect the automation list."""
    return Event(
        EventRequest(
            type=EventType.SHOW_NOTE_BODY_AUTOMATIONS,
            context=json.dumps({"note_id": 1234, "user": {"type": "Staff", "id": "abc"}}),
        )
    )


def _selected_event(key: str) -> Event:
    """Build the event Canvas fires when the user selects an automation."""
    return Event(
        EventRequest(
            type=EventType.NOTE_BODY_AUTOMATION_SELECTED,
            context=json.dumps({"key": key, "note_id": 1234}),
        )
    )


# --- RESPONDS_TO ---


def test_responds_to_both_events() -> None:
    """The handler subscribes to the list event and the selection event."""
    assert NoteBodyAutomation.RESPONDS_TO == [
        "SHOW_NOTE_BODY_AUTOMATIONS",
        "NOTE_BODY_AUTOMATION_SELECTED",
    ]
    assert SHOW_AUTOMATIONS_EVENT == "SHOW_NOTE_BODY_AUTOMATIONS"
    assert AUTOMATION_SELECTED_EVENT == "NOTE_BODY_AUTOMATION_SELECTED"


# --- configuration guard ---


def test_missing_key_raises() -> None:
    """A subclass with no AUTOMATION_KEY fails at class definition."""
    with pytest.raises(ImproperlyConfigured, match="must define AUTOMATION_KEY"):

        class NoKeyAutomation(NoteBodyAutomation):
            AUTOMATION_TITLE = "No Key"

            def handle(self) -> list[Effect]:
                return []


def test_missing_title_raises() -> None:
    """A subclass with no AUTOMATION_TITLE fails at class definition."""
    with pytest.raises(ImproperlyConfigured, match="must define AUTOMATION_TITLE"):

        class NoTitleAutomation(NoteBodyAutomation):
            AUTOMATION_KEY = "no_title"

            def handle(self) -> list[Effect]:
                return []


def test_empty_key_raises() -> None:
    """An empty AUTOMATION_KEY fails the same way a missing one does."""
    with pytest.raises(ImproperlyConfigured, match="must define AUTOMATION_KEY"):

        class EmptyKeyAutomation(NoteBodyAutomation):
            AUTOMATION_KEY = ""
            AUTOMATION_TITLE = "Empty Key"

            def handle(self) -> list[Effect]:
                return []


# --- defaults ---


def test_default_visible_returns_true() -> None:
    """An automation shows unless the subclass says otherwise."""
    assert ExampleAutomation(_show_event()).visible() is True


def test_keywords_and_priority_defaults() -> None:
    """KEYWORDS defaults to empty and PRIORITY defaults to zero."""
    assert InvisibleAutomation.KEYWORDS == []
    assert InvisibleAutomation.PRIORITY == 0


# --- compute() on the list event ---


def test_compute_show_event_returns_one_effect() -> None:
    """The list event returns one SHOW_NOTE_BODY_AUTOMATION effect."""
    effects = ExampleAutomation(_show_event()).compute()

    assert len(effects) == 1
    assert effects[0].type == EffectType.SHOW_NOTE_BODY_AUTOMATION


def test_compute_show_event_effect_payload() -> None:
    """The effect payload carries the key, title, keywords and priority."""
    effects = ExampleAutomation(_show_event()).compute()

    assert json.loads(effects[0].payload) == {
        "data": {
            "key": "test_automation",
            "title": "Test Automation",
            "keywords": ["test", "example"],
            "priority": 5,
        }
    }


def test_compute_show_event_hidden_automation() -> None:
    """An automation that is not visible contributes no effect."""
    assert InvisibleAutomation(_show_event()).compute() == []


# --- compute() on the selection event ---


def test_compute_selected_event_matching_key_runs_handle() -> None:
    """A selection for this automation's key runs handle()."""
    effects = ExampleAutomation(_selected_event("test_automation")).compute()

    assert effects == [_HANDLE_EFFECT]


def test_compute_selected_event_other_key_does_nothing() -> None:
    """A selection for another automation's key runs nothing."""
    assert ExampleAutomation(_selected_event("some_other_key")).compute() == []


def test_compute_selected_event_without_key_does_nothing() -> None:
    """A selection event with no key in the context runs nothing."""
    event = Event(
        EventRequest(
            type=EventType.NOTE_BODY_AUTOMATION_SELECTED,
            context=json.dumps({"note_id": 1234}),
        )
    )

    assert ExampleAutomation(event).compute() == []


def test_compute_hidden_automation_still_handles_selection() -> None:
    """visible() gates the list only. A selection always reaches handle()."""
    with patch.object(InvisibleAutomation, "handle", return_value=[_HANDLE_EFFECT]) as handle:
        effects = InvisibleAutomation(_selected_event("hidden_automation")).compute()

    assert effects == [_HANDLE_EFFECT]
    handle.assert_called_once()


# --- note lookup ---


def test_note_is_none_without_note_id() -> None:
    """The note is None when the context carries no note_id."""
    event = Event(EventRequest(type=EventType.SHOW_NOTE_BODY_AUTOMATIONS, context=json.dumps({})))

    assert ExampleAutomation(event).note is None


def test_note_looks_up_by_dbid() -> None:
    """The note lookup uses dbid, because Canvas sends the note's database id."""
    expected = MagicMock()
    with patch("canvas_sdk.handlers.note_body_automation.Note.objects.filter") as note_filter:
        select_related = note_filter.return_value.select_related
        select_related.return_value.first.return_value = expected
        automation = ExampleAutomation(_show_event())

        assert automation.note is expected
        assert automation.note is expected  # cached, so only one query

    note_filter.assert_called_once_with(dbid=1234)
    select_related.assert_called_once_with("note_type_version")


# --- effect validation ---


def test_effect_rejects_empty_key() -> None:
    """The effect refuses an empty key, which would never match a selection."""
    with pytest.raises(ValidationError):
        ShowNoteBodyAutomationEffect(key="", title="Title")


def test_effect_rejects_empty_title() -> None:
    """The effect refuses an empty title, which would show a blank entry."""
    with pytest.raises(ValidationError):
        ShowNoteBodyAutomationEffect(key="key", title="")


def test_effect_defaults() -> None:
    """The effect defaults to no keywords and priority zero."""
    effect = ShowNoteBodyAutomationEffect(key="key", title="Title")

    assert effect.values == {"key": "key", "title": "Title", "keywords": [], "priority": 0}
