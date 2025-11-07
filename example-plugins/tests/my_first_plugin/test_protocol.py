"""Comprehensive tests for my_first_plugin."""

import json
from unittest.mock import Mock, patch

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.events import EventType


def test_import_protocol():
    """Test that Protocol can be imported without errors."""
    from my_first_plugin.protocols.protocol import Protocol

    # Verify the class exists and has expected attributes
    assert Protocol is not None
    assert hasattr(Protocol, "RESPONDS_TO")
    assert hasattr(Protocol, "compute")
    assert hasattr(Protocol, "NARRATIVE_STRING")


def test_protocol_configuration():
    """Test that Protocol has correct configuration."""
    from my_first_plugin.protocols.protocol import Protocol

    # Verify configuration
    assert Protocol.RESPONDS_TO == EventType.Name(EventType.ASSESS_COMMAND__CONDITION_SELECTED)
    assert Protocol.NARRATIVE_STRING == "zebra"


def test_compute_creates_log_effect():
    """Test that compute method creates a LOG effect with correct payload."""
    from my_first_plugin.protocols.protocol import Protocol

    # Create mock event
    mock_event = Mock()
    mock_event.context = {"note": {"uuid": "test-note-uuid-123"}}

    # Create protocol instance
    protocol = Protocol(event=mock_event)  # type: ignore[arg-type]

    # Mock the logger to prevent actual logging
    with patch("my_first_plugin.protocols.protocol.log"):
        result = protocol.compute()

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


def test_compute_logs_narrative_string():
    """Test that compute method logs the narrative string."""
    from my_first_plugin.protocols.protocol import Protocol

    # Create mock event
    mock_event = Mock()
    mock_event.context = {"note": {"uuid": "another-uuid"}}

    # Create protocol instance
    protocol = Protocol(event=mock_event)  # type: ignore[arg-type]

    # Mock the logger and verify it's called with NARRATIVE_STRING
    with patch("my_first_plugin.protocols.protocol.log") as mock_log:
        protocol.compute()

        # Verify log.info was called with "zebra"
        mock_log.info.assert_called_once_with("zebra")
