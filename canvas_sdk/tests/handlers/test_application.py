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

    def on_context_change(self) -> Effect | None:
        """Handle the application context change event by returning a mock effect."""
        return LaunchModalEffect(url="https://example.com/context").apply()


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


def test_compute_context_change_event_not_targeted() -> None:
    """Test that compute filters out context change events not targeted for the app."""
    request = EventRequest(type=EventType.APPLICATION__ON_CONTEXT_CHANGE, target="some_identifier")
    event = Event(request)
    app = ExampleApplication(event)

    result = app.compute()

    assert result == [], "Expected no effects if the event target is not the app identifier"


def test_compute_context_change_event_targeted() -> None:
    """Test that compute processes context change events targeted for the app."""
    request = EventRequest(
        type=EventType.APPLICATION__ON_CONTEXT_CHANGE,
        target=f"{ExampleApplication.__module__}:{ExampleApplication.__qualname__}",
    )
    event = Event(request)
    app = ExampleApplication(event)
    result = app.compute()

    assert len(result) == 1, "Expected a single effect if the event target is the app identifier"
    assert isinstance(result[0], Effect), "Effect should be an instance of Effect"


class EffectsList(Application):
    """A concrete implementation of the Application class for testing."""

    def on_open(self) -> Effect | list[Effect]:
        """Handle the application open event by returning a mock effect."""
        return [LaunchModalEffect(url="https://example.com").apply()]

    def on_context_change(self) -> Effect | list[Effect] | None:
        """Handle the application context change event by returning a mock effect."""
        return [LaunchModalEffect(url="https://example.com/context").apply()]


class MultipleEffectsList(Application):
    """A concrete implementation of the Application class for testing."""

    def on_open(self) -> Effect | list[Effect]:
        """Handle the application open event by returning a mock effect."""
        return [
            LaunchModalEffect(url="https://example.com").apply(),
            LaunchModalEffect(url="https://canvasmedical.com").apply(),
        ]

    def on_context_change(self) -> Effect | list[Effect] | None:
        """Handle the application context change event by returning a mock effect."""
        return [
            LaunchModalEffect(url="https://example.com/context").apply(),
            LaunchModalEffect(url="https://canvasmedical.com").apply(),
        ]


class MultipleEffectsListWithInvalids(Application):
    """A concrete implementation of the Application class for testing."""

    def on_open(self) -> Effect | list[Effect]:
        """Handle the application open event by returning a mock effect."""
        return [
            {"not": "an effect"},  # type: ignore
            LaunchModalEffect(url="https://canvasmedical.com").apply(),
        ]

    def on_context_change(self) -> Effect | list[Effect] | None:
        """Handle the application context change event by returning a mock effect."""
        return [
            {"not": "an effect"},  # type: ignore
            {"also": "not an effect"},  # type: ignore
        ]


@pytest.mark.parametrize(
    "event_type,App,exp_num_effects",
    [
        (EventType.APPLICATION__ON_OPEN, EffectsList, 1),
        (EventType.APPLICATION__ON_CONTEXT_CHANGE, EffectsList, 1),
        (EventType.APPLICATION__ON_OPEN, MultipleEffectsList, 2),
        (EventType.APPLICATION__ON_CONTEXT_CHANGE, MultipleEffectsList, 2),
        (EventType.APPLICATION__ON_OPEN, MultipleEffectsListWithInvalids, 1),
        (EventType.APPLICATION__ON_CONTEXT_CHANGE, MultipleEffectsListWithInvalids, 0),
    ],
    ids=(
        "on-open-single",
        "on-context-change-single",
        "on-open-multiple",
        "on-context-change-multiple",
        "on-open-multiple-with-invalids",
        "on-context-change-multiple-with-invalids",
    ),
)
def test_compute_with_list_effects(
    event_type: EventType, App: type[Application], exp_num_effects: int
) -> None:
    """Ensure compute normalizes on_open return values to a list of Effects."""
    request = EventRequest(
        type=event_type,
        target=f"{App.__module__}:{App.__qualname__}",
    )
    effects = App(Event(request)).compute()
    assert len(effects) == exp_num_effects
    for effect in effects:
        assert isinstance(effect, Effect)


def test_normalize_effects_none() -> None:
    """normalize_effects should return an empty list when given None."""
    from canvas_sdk.handlers.utils import normalize_effects

    assert normalize_effects(None) == []


def test_normalize_effects_single_effect() -> None:
    """normalize_effects should wrap a single Effect into a list."""
    from canvas_sdk.handlers.utils import normalize_effects

    eff = LaunchModalEffect(url="https://example.com").apply()
    res = normalize_effects(eff)
    assert isinstance(res, list)
    assert len(res) == 1
    assert res[0] is eff


def test_normalize_effects_list_with_invalids() -> None:
    """normalize_effects should filter out non-Effect items from a list."""
    from canvas_sdk.handlers.utils import normalize_effects

    eff = LaunchModalEffect(url="https://example.com").apply()
    mixed = [{"not": "an effect"}, eff, 123]
    res = normalize_effects(mixed)  # type: ignore[arg-type]
    assert res == [eff]
