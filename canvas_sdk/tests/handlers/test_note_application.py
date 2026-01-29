import json

import pytest

from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.handlers.action_button import ActionButton
from canvas_sdk.handlers.application import NoteApplication


class ExampleNoteApplication(NoteApplication):
    """A concrete implementation of NoteApplication for testing."""

    NAME = "Test Application"
    IDENTIFIER = "test_plugin__test_app"

    def handle(self) -> list[Effect]:
        """Handle the button click by returning a mock effect."""
        return [LaunchModalEffect(url="https://example.com").apply()]


def test_note_application_properties() -> None:
    """Test that NoteApplication properties map correctly from class attributes."""
    request = EventRequest(type=EventType.ACTION_BUTTON_CLICKED)
    event = Event(request)
    app = ExampleNoteApplication(event)

    assert app.NAME == "Test Application"
    assert app.IDENTIFIER == "test_plugin__test_app"
    assert app.BUTTON_TITLE == "Test Application"
    assert app.BUTTON_KEY == "test_plugin__test_app"
    assert app.BUTTON_LOCATION == ActionButton.ButtonLocation.NOTE_BODY

    with pytest.raises(AttributeError):
        app.BUTTON_LOCATION = ActionButton.ButtonLocation.NOTE_HEADER  # type: ignore[misc]


def test_compute_handles_action_button_clicked_with_matching_key() -> None:
    """Test that compute calls handle() when action button clicked matches key."""
    context = json.dumps({"key": "test_plugin__test_app"})
    request = EventRequest(type=EventType.ACTION_BUTTON_CLICKED, context=context)
    event = Event(request)
    app = ExampleNoteApplication(event)

    result = app.compute()

    assert len(result) == 1
    assert isinstance(result[0], Effect)


def test_compute_returns_empty_when_key_does_not_match() -> None:
    """Test that compute returns empty list when clicked key doesn't match."""
    context = json.dumps({"key": "different_key"})
    request = EventRequest(type=EventType.ACTION_BUTTON_CLICKED, context=context)
    event = Event(request)
    app = ExampleNoteApplication(event)

    assert app.compute() == []


def test_note_application_responds_to_includes_action_button_clicked() -> None:
    """Test that NoteApplication responds to ACTION_BUTTON_CLICKED events."""
    assert EventType.Name(EventType.ACTION_BUTTON_CLICKED) in NoteApplication.RESPONDS_TO
