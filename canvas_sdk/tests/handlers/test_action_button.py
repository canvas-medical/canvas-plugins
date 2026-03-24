import json

from canvas_sdk.effects import Effect
from canvas_sdk.effects.show_button import ShowButtonEffect
from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.handlers.action_button import SHOW_BUTTON_REGEX, ActionButton


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
        "SHOW_PATIENT_HEADER_BUTTON": "PATIENT_HEADER",
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
    assert "SHOW_PATIENT_HEADER_BUTTON" in ActionButton.RESPONDS_TO


# --- ButtonLocation enum tests ---


def test_button_location_enum_values() -> None:
    """Test that ButtonLocation enum has expected values."""
    assert ActionButton.ButtonLocation.NOTE_HEADER.value == "note_header"
    assert ActionButton.ButtonLocation.NOTE_FOOTER.value == "note_footer"
    assert ActionButton.ButtonLocation.NOTE_BODY.value == "note_body"
    assert ActionButton.ButtonLocation.PATIENT_HEADER.value == "patient_header"


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
