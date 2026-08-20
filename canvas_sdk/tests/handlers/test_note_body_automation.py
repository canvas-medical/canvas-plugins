import json
from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ImproperlyConfigured
from pydantic import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.commands.commands.plan import PlanCommand
from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.effects.note_body_automation import ShowNoteBodyAutomationEffect
from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.handlers.note_body_automation import (
    AUTOMATION_SELECTED_EVENT,
    DEFAULT_LINE_NUMBER,
    SHOW_AUTOMATIONS_EVENT,
    NoteBodyAutomation,
)

NOTE_UUID = "6a1b0d0e-0000-4000-8000-000000000000"

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


def _selected_event(key: str, line_number: int | None = 7) -> Event:
    """Build the event Canvas fires when the user selects an automation."""
    context: dict = {"key": key, "note_id": 1234}
    if line_number is not None:
        context["line_number"] = line_number
    return Event(
        EventRequest(type=EventType.NOTE_BODY_AUTOMATION_SELECTED, context=json.dumps(context))
    )


class OriginatingAutomation(NoteBodyAutomation):
    """An automation that adds a command, the way a real one does."""

    AUTOMATION_KEY = "originating_automation"
    AUTOMATION_TITLE = "Originating Automation"

    line_for_the_command: int | None = None

    def handle(self) -> list[Effect]:
        """Add a Plan command, with a line only when the test asks for one."""
        command = PlanCommand(note_uuid=NOTE_UUID, narrative="Follow up.")
        if self.line_for_the_command is None:
            return [command.originate()]
        return [command.originate(line_number=self.line_for_the_command)]


def _originated_line(effects: list[Effect]) -> int:
    """The line number in the one origination among ``effects``."""
    return json.loads(effects[0].payload)["line_number"]


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


# --- the line the user typed on ---


def test_line_number_comes_from_the_context() -> None:
    """The handler exposes the line Canvas sent, for an author who wants it."""
    assert ExampleAutomation(_selected_event("test_automation", line_number=3)).line_number == 3


def test_line_number_defaults_to_the_appending_value() -> None:
    """With no line in the context the handler reports the appending default."""
    event = _selected_event("test_automation", line_number=None)

    assert ExampleAutomation(event).line_number == DEFAULT_LINE_NUMBER


def test_a_command_lands_on_the_line_the_user_typed_on() -> None:
    """An automation writes plain originate(), and Canvas still gets the user's line."""
    automation = OriginatingAutomation(_selected_event("originating_automation", line_number=7))

    effects = automation.compute()

    assert _originated_line(effects) == 7


def test_a_line_the_author_chose_is_kept() -> None:
    """An author who asks for a specific line keeps it."""
    automation = OriginatingAutomation(_selected_event("originating_automation", line_number=7))
    automation.line_for_the_command = 2

    effects = automation.compute()

    assert _originated_line(effects) == 2


def test_a_command_appends_when_the_context_carries_no_line() -> None:
    """With no line to place it on, the command keeps the appending default."""
    automation = OriginatingAutomation(_selected_event("originating_automation", line_number=None))

    effects = automation.compute()

    assert _originated_line(effects) == DEFAULT_LINE_NUMBER


def test_another_effect_is_left_alone() -> None:
    """Only a command origination is placed. Every other effect passes through."""
    modal = LaunchModalEffect(content="<p>hi</p>", title="Summary").apply()
    payload_before = modal.payload

    class ModalAutomation(NoteBodyAutomation):
        AUTOMATION_KEY = "modal_automation"
        AUTOMATION_TITLE = "Modal Automation"

        def handle(self) -> list[Effect]:
            return [modal]

    effects = ModalAutomation(_selected_event("modal_automation", line_number=7)).compute()

    assert effects[0].payload == payload_before
