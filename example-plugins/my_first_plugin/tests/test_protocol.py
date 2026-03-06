"""Comprehensive tests for my_first_plugin."""

import json
from unittest.mock import Mock, patch

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.events import EventType


def test_import_protocol() -> None:
    """Test that Handler can be imported without errors."""
    from my_first_plugin.handlers.handler import Handler

    # Verify the class exists and has expected attributes
    assert Handler is not None
    assert hasattr(Handler, "RESPONDS_TO")
    assert hasattr(Handler, "compute")
    assert hasattr(Handler, "NARRATIVE_STRING")


def test_protocol_configuration() -> None:
    """Test that Handler has correct configuration."""
    from my_first_plugin.handlers.handler import Handler

    # Verify configuration
    assert EventType.Name(EventType.ASSESS_COMMAND__CONDITION_SELECTED) == Handler.RESPONDS_TO
    assert Handler.NARRATIVE_STRING == "zebra"


def test_compute_creates_log_effect() -> None:
    """Test that compute method creates a LOG effect with correct payload."""
    from my_first_plugin.handlers.handler import Handler

    # Create mock event
    mock_event = Mock()
    mock_event.context = {"note": {"uuid": "test-note-uuid-123"}}

    # Create handler instance
    handler = Handler(event=mock_event)

    # Mock the logger to prevent actual logging
    with patch("my_first_plugin.handlers.handler.log"):
        result = handler.compute()

    # Verify result is a list with one effect
    assert len(result) == 1
    assert isinstance(result[0], Effect)

    # Verify effect type
    assert result[0].type == EffectType.LOG

    # Verify effect payload
    payload = json.loads(result[0].payload)
    assert payload == {
        "note": {"uuid": "test-note-uuid-123"},
        "data": {"narrative": "zebra"},
    }


def test_compute_logs_narrative_string() -> None:
    """Test that compute method logs the narrative string."""
    from my_first_plugin.handlers.handler import Handler

    # Create mock event
    mock_event = Mock()
    mock_event.context = {"note": {"uuid": "another-uuid"}}

    # Create handler instance
    handler = Handler(event=mock_event)

    # Mock the logger and verify it's called with NARRATIVE_STRING
    with patch("my_first_plugin.handlers.handler.log") as mock_log:
        handler.compute()

        # Verify log.info was called with "zebra"
        mock_log.info.assert_called_once_with("zebra")
