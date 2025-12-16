"""Tests for the simple demo plugin protocol.

To run tests: uv run pytest
To run with coverage: uv run pytest --cov=simple_demo_plugin --cov-report=term-missing

Each test is wrapped inside a transaction that is rolled back at the end of the test.
For more information on testing Canvas plugins, see: https://docs.canvasmedical.com/sdk/testing-utils/
"""

from unittest.mock import Mock, patch

from canvas_sdk.effects.banner_alert import AddBannerAlert
from canvas_sdk.events import EventType

from simple_demo_plugin.protocols.my_protocol import Protocol


def test_protocol_event_configuration() -> None:
    """Test that the protocol is configured to respond to PATIENT_UPDATED events."""
    assert EventType.Name(EventType.PATIENT_UPDATED) == Protocol.RESPONDS_TO


def test_protocol_returns_banner_alert() -> None:
    """Test that the protocol returns an AddBannerAlert effect when a patient is updated."""
    # Create a mock event
    mock_event = Mock()
    mock_event.type = EventType.PATIENT_UPDATED
    mock_event.target = Mock()
    mock_event.target.id = "test-patient-123"
    mock_event.context = {}

    # Instantiate the protocol with the mock event
    protocol = Protocol(event=mock_event)

    # Call compute and get the effects
    effects = protocol.compute()

    # Assert that exactly one effect was returned
    assert len(effects) == 1

    # Assert the effect has the correct type (it's an Effect object after .apply())
    effect = effects[0]
    assert hasattr(effect, "type")
    assert hasattr(effect, "payload")


@patch("simple_demo_plugin.protocols.my_protocol.log")
def test_protocol_logs_event_info(mock_log: Mock) -> None:
    """Test that the protocol logs event information."""
    # Create a mock event
    mock_event = Mock()
    mock_event.type = EventType.PATIENT_UPDATED
    mock_event.target = Mock()
    mock_event.target.id = "test-patient-456"
    mock_event.context = {}

    # Instantiate the protocol and call compute
    protocol = Protocol(event=mock_event)
    protocol.compute()

    # Assert that log.info was called with patient ID
    mock_log.info.assert_called_once()
    call_args = mock_log.info.call_args[0][0]
    assert "test-patient-456" in call_args
    assert "Patient updated" in call_args


def test_protocol_always_returns_banner() -> None:
    """Test that the protocol always returns a banner alert."""
    # Create a minimal mock event
    mock_event = Mock()
    mock_event.type = EventType.PATIENT_UPDATED
    mock_event.target = Mock()
    mock_event.target.id = "123"
    mock_event.context = {}

    # Instantiate the protocol with the mock event
    protocol = Protocol(event=mock_event)

    # Call compute and get the effects
    effects = protocol.compute()

    # Should always return exactly one effect
    assert len(effects) == 1
    assert hasattr(effects[0], "type")
    assert hasattr(effects[0], "payload")
