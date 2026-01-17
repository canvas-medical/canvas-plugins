import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from preact_hello_world.protocols.counter_button import CounterButton

from canvas_sdk.handlers.action_button import ActionButton

COUNTER_HTML = (
    Path(__file__).parent.parent.parent / "preact_hello_world" / "templates" / "counter.html"
).read_text()


class TestCounterButtonConfiguration:
    """Tests for ActionButton configuration."""

    def test_button_title(self) -> None:
        """Button title should be 'Counter Demo'."""
        assert CounterButton.BUTTON_TITLE == "Counter Demo"

    def test_button_key(self) -> None:
        """Button key should be 'COUNTER_DEMO'."""
        assert CounterButton.BUTTON_KEY == "COUNTER_DEMO"

    def test_button_location(self) -> None:
        """Button should appear in note header."""
        assert CounterButton.BUTTON_LOCATION == ActionButton.ButtonLocation.NOTE_HEADER


@patch("preact_hello_world.protocols.counter_button.render_to_string", return_value=COUNTER_HTML)
class TestCounterButtonHandle:
    """Tests for handle() method."""

    def test_handle_returns_launch_modal_effect(
        self, mock_render: MagicMock, mock_event: MagicMock
    ) -> None:
        """handle() should return a LaunchModalEffect for the right chart pane."""
        handler = CounterButton(event=mock_event)

        effects = handler.handle()

        # Verify mock_event was not accessed (handle doesn't use event)
        assert mock_event.mock_calls == []

        # Verify output - one effect returned
        assert len(effects) == 1
        effect = effects[0]
        # Effect type 3000 is LAUNCH_MODAL_EFFECT
        assert effect.type == 3000

    def test_handle_effect_has_correct_target(
        self, mock_render: MagicMock, mock_event: MagicMock
    ) -> None:
        """Effect should target RIGHT_CHART_PANE."""
        handler = CounterButton(event=mock_event)

        effects = handler.handle()

        # Verify mock_event was not accessed
        assert mock_event.mock_calls == []

        # Verify effect target in payload
        effect = effects[0]
        payload = json.loads(effect.payload)
        assert payload["data"]["target"] == "right_chart_pane"

    def test_handle_effect_has_correct_title(
        self, mock_render: MagicMock, mock_event: MagicMock
    ) -> None:
        """Effect should have title 'Counter Demo'."""
        handler = CounterButton(event=mock_event)

        effects = handler.handle()

        # Verify mock_event was not accessed
        assert mock_event.mock_calls == []

        # Verify effect title in payload
        effect = effects[0]
        payload = json.loads(effect.payload)
        assert payload["data"]["title"] == "Counter Demo"

    def test_handle_effect_contains_html_content(
        self, mock_render: MagicMock, mock_event: MagicMock
    ) -> None:
        """Effect should contain the bundled HTML content."""
        handler = CounterButton(event=mock_event)

        effects = handler.handle()

        # Verify mock_event was not accessed
        assert mock_event.mock_calls == []

        # Verify effect content in payload matches the constant
        effect = effects[0]
        payload = json.loads(effect.payload)
        assert payload["data"]["content"] == COUNTER_HTML


class TestCounterHTML:
    """Tests for the bundled HTML content."""

    def test_html_contains_doctype(self) -> None:
        """HTML should start with DOCTYPE."""
        assert COUNTER_HTML.startswith("<!DOCTYPE html>")

    def test_html_contains_app_div(self) -> None:
        """HTML should contain the app mount point."""
        assert '<div id="app">' in COUNTER_HTML

    def test_html_contains_preact_code(self) -> None:
        """HTML should contain bundled Preact code."""
        assert "counter-container" in COUNTER_HTML
        assert "Hello World" in COUNTER_HTML
