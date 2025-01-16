import pytest

from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.handlers.application import Application


class ExampleApplication(Application):
    """A concrete implementation of the Application class for testing."""

    def on_open(self) -> Effect:
        """Handle the application open event by returning a mock effect."""
        return LaunchModalEffect(url="https://example.com").apply()


@pytest.fixture
def app_instance(event: Event) -> ExampleApplication:
    """Provide an instance of the TestApplication with a mocked event."""
    app = ExampleApplication(event)
    return app


def test_compute_event_not_targeted() -> None:
    """Test that compute filters out events not targeted for the app."""
    request = EventRequest(type=EventType.APPLICATION__ON_OPEN, target="some_identifier")
    event = Event(request)
    app = ExampleApplication(event)

    result = app.compute()

    assert result == [], "Expected no effects if the event target is not the app identifier"


def test_compute_event_targeted() -> None:
    """Test that compute processes events targeted for the app."""
    request = EventRequest(
        type=EventType.APPLICATION__ON_OPEN,
        target=f"{ExampleApplication.__module__}:{ExampleApplication.__qualname__}",
    )
    event = Event(request)
    app = ExampleApplication(event)
    result = app.compute()

    assert len(result) == 1, "Expected a single effect if the event target is the app identifier"
    assert isinstance(result[0], Effect), "Effect should be an instance of Effect"


def test_identifier_property() -> None:
    """Test the identifier property of the Application class."""
    expected_identifier = f"{ExampleApplication.__module__}:{ExampleApplication.__qualname__}"
    request = EventRequest(
        type=EventType.APPLICATION__ON_OPEN,
        target=f"{ExampleApplication.__module__}:{ExampleApplication.__qualname__}",
    )
    event = Event(request)
    app = ExampleApplication(event)

    assert app.identifier == expected_identifier, "The identifier property is incorrect"


def test_abstract_method_on_open() -> None:
    """Test that the abstract method on_open must be implemented."""
    with pytest.raises(TypeError):
        Application(Event(EventRequest(type=EventType.UNKNOWN)))  # type: ignore[abstract]
