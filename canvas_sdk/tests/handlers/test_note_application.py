import json
import warnings

import pytest

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.handlers.application import ApplicationScope, NoteApplication


class OldNoteApplication(NoteApplication):
    """A NoteApplication using the deprecated handle() method."""

    NAME = "Old App"
    IDENTIFIER = "test_plugin__old_app"

    def handle(self) -> list[Effect]:
        """Handle a note application click."""
        return [LaunchModalEffect(url="https://example.com/old").apply()]


class NewNoteApplication(NoteApplication):
    """A NoteApplication using the new on_open() method."""

    NAME = "New App"
    IDENTIFIER = "test_plugin__new_app"

    def on_open(self) -> list[Effect]:
        """On open method."""
        return [LaunchModalEffect(url="https://example.com/new").apply()]


class DefaultOpenNoteApplication(NoteApplication):
    """A NoteApplication that opens by default."""

    NAME = "Default Open App"
    IDENTIFIER = "test_plugin__default_open"
    PRIORITY = 5

    def open_by_default(self) -> bool:
        """Open a note application by default."""
        return True

    def on_open(self) -> list[Effect]:
        """Open a note application by default."""
        return [LaunchModalEffect(url="https://example.com/default").apply()]


class HiddenNoteApplication(NoteApplication):
    """A NoteApplication that is not visible."""

    NAME = "Hidden App"
    IDENTIFIER = "test_plugin__hidden"

    def visible(self) -> bool:
        """Visible note application."""
        return False

    def on_open(self) -> list[Effect]:
        """On open method."""
        return []


class AlwaysVisibleNoteApplication(NoteApplication):
    """A NoteApplication that overrides visible() to always return True."""

    NAME = "Always Visible App"
    IDENTIFIER = "test_plugin__always_visible"

    def visible(self) -> bool:
        """Always visible."""
        return True

    def on_open(self) -> list[Effect]:
        """On open method."""
        return []


class NoIdentifierNoteApplication(NoteApplication):
    """A NoteApplication without an explicit IDENTIFIER."""

    NAME = "No ID App"

    def on_open(self) -> list[Effect]:
        """On open method."""
        return []


def _make_event(
    event_type: EventType,
    target: str = "",
    context: dict | None = None,
) -> Event:
    """Create an Event from the given type, target, and context."""
    return Event(
        EventRequest(
            type=event_type,
            target=target,
            context=json.dumps(context or {}),
        )
    )


def _make_on_get_event(scope: str = "note") -> Event:
    """Create an APPLICATION__ON_GET event with the given scope."""
    return _make_event(EventType.APPLICATION__ON_GET, context={"scope": scope})


def _make_on_open_event(target: str) -> Event:
    """Create an APPLICATION__ON_OPEN event targeting the given identifier."""
    return _make_event(EventType.APPLICATION__ON_OPEN, target=target)


def test_note_application_scope_and_responds_to() -> None:
    """Verify NoteApplication has the correct scope and responds to all application events."""
    assert NoteApplication.SCOPE == ApplicationScope.NOTE
    assert EventType.Name(EventType.APPLICATION__ON_OPEN) in NoteApplication.RESPONDS_TO
    assert EventType.Name(EventType.APPLICATION__ON_CONTEXT_CHANGE) in NoteApplication.RESPONDS_TO
    assert EventType.Name(EventType.APPLICATION__ON_GET) in NoteApplication.RESPONDS_TO


@pytest.mark.parametrize(
    "app_class,expected_identifier",
    [
        (OldNoteApplication, "test_plugin__old_app"),
        (
            NoIdentifierNoteApplication,
            f"{NoIdentifierNoteApplication.__module__}:{NoIdentifierNoteApplication.__qualname__}",
        ),
    ],
    ids=["explicit-identifier", "fallback-to-module-qualname"],
)
def test_identifier_resolution(app_class: type[NoteApplication], expected_identifier: str) -> None:
    """Verify identifier uses IDENTIFIER when set, otherwise falls back to module:qualname."""
    app = app_class(_make_on_get_event())
    assert app.identifier == expected_identifier


def test_on_get_returns_show_application_effect() -> None:
    """Verify ON_GET returns a SHOW_APPLICATION effect with the correct payload."""
    app = NewNoteApplication(_make_on_get_event(scope="note"))
    result = app.compute()

    assert len(result) == 1
    assert result[0].type == EffectType.SHOW_APPLICATION
    payload = json.loads(result[0].payload)["data"]
    assert payload["name"] == "New App"
    assert payload["identifier"] == "test_plugin__new_app"
    assert payload["open_by_default"] is False
    assert payload["priority"] == 0


def test_on_get_respects_open_by_default_and_priority() -> None:
    """Verify ON_GET includes open_by_default and priority in the effect payload."""
    app = DefaultOpenNoteApplication(_make_on_get_event(scope="note"))
    result = app.compute()

    payload = json.loads(result[0].payload)["data"]
    assert payload["open_by_default"] is True
    assert payload["priority"] == 5


@pytest.mark.parametrize(
    "app_class,scope,reason",
    [
        (NewNoteApplication, "chart", "scope does not match"),
        (HiddenNoteApplication, "note", "visible() returns False"),
        (AlwaysVisibleNoteApplication, "chart", "scope mismatch cannot be bypassed by visible()"),
    ],
    ids=["wrong-scope", "not-visible", "scope-bypass-prevented"],
)
def test_on_get_returns_empty(app_class: type[NoteApplication], scope: str, reason: str) -> None:
    """Verify ON_GET returns no effects when the application should not be shown."""
    app = app_class(_make_on_get_event(scope=scope))
    assert app.compute() == [], reason


@pytest.mark.parametrize(
    "app_class,target",
    [
        (OldNoteApplication, "test_plugin__old_app"),
        (NewNoteApplication, "test_plugin__new_app"),
    ],
    ids=["old-plugin-via-handle", "new-plugin-via-on-open"],
)
def test_on_open_returns_effects(app_class: type[NoteApplication], target: str) -> None:
    """Verify ON_OPEN returns effects for both old (handle) and new (on_open) plugins."""
    app = app_class(_make_on_open_event(target))
    result = app.compute()

    assert len(result) == 1
    assert result[0].type == EffectType.LAUNCH_MODAL


def test_on_open_returns_empty_when_target_does_not_match() -> None:
    """Verify ON_OPEN returns no effects when the target identifier does not match."""
    app = NewNoteApplication(_make_on_open_event(target="wrong_identifier"))
    assert app.compute() == []


@pytest.mark.parametrize(
    "target",
    ["test_plugin__new_app", "wrong_target"],
    ids=["matching-target", "wrong-target"],
)
def test_on_context_change_returns_empty_by_default(target: str) -> None:
    """Verify ON_CONTEXT_CHANGE returns no effects by default (no override)."""
    event = _make_event(EventType.APPLICATION__ON_CONTEXT_CHANGE, target=target)
    app = NewNoteApplication(event)
    assert app.compute() == []


def test_handle_emits_deprecation_warning() -> None:
    """Verify calling handle() directly emits a DeprecationWarning pointing to on_open."""
    app = NewNoteApplication(_make_on_get_event())
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        app.handle()
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "on_open" in str(w[0].message)
