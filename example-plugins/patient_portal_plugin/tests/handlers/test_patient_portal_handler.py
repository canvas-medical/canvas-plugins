"""Tests for patient_portal_plugin.handlers.patient_portal_handler module."""

from unittest.mock import MagicMock

from patient_portal_plugin.handlers.patient_portal_handler import PatientPortalHandler


class TestPatientPortalHandler:
    """Tests for PatientPortalHandler class."""

    def test_responds_to_configuration(self):
        """Test that handler responds to the correct event type."""
        from canvas_sdk.events import EventType

        assert PatientPortalHandler.RESPONDS_TO == EventType.Name(
            EventType.PATIENT_PORTAL__WIDGET_CONFIGURATION
        )

    def test_inherits_from_base_handler(self):
        """Test that PatientPortalHandler inherits from BaseHandler."""
        from canvas_sdk.handlers.base import BaseHandler

        assert issubclass(PatientPortalHandler, BaseHandler)

    def test_default_background_color(self):
        """Test that default background color is set correctly."""
        assert PatientPortalHandler.DEFAULT_BACKGROUND_COLOR == "#17634d"

    def test_default_emergency_contact(self):
        """Test that default emergency contact is set correctly."""
        assert PatientPortalHandler.DEFAULT_EMERGENCY_CONTACT == "1-888-555-5555"

    def test_background_color_from_secrets(self):
        """Test that background_color returns value from secrets."""
        mock_event = MagicMock()
        handler = PatientPortalHandler(event=mock_event)
        handler.secrets = {"BACKGROUND_COLOR": "#ff0000"}

        assert handler.background_color == "#ff0000"

    def test_background_color_default(self):
        """Test that background_color returns default when not in secrets."""
        mock_event = MagicMock()
        handler = PatientPortalHandler(event=mock_event)
        handler.secrets = {}

        assert handler.background_color == "#17634d"

    def test_emergency_contact_from_secrets(self):
        """Test that emergency_contact returns value from secrets."""
        mock_event = MagicMock()
        handler = PatientPortalHandler(event=mock_event)
        handler.secrets = {"EMERGENCY_CONTACT": "1-800-DOCTOR"}

        assert handler.emergency_contact == "1-800-DOCTOR"

    def test_emergency_contact_default(self):
        """Test that emergency_contact returns default when not in secrets."""
        mock_event = MagicMock()
        handler = PatientPortalHandler(event=mock_event)
        handler.secrets = {}

        assert handler.emergency_contact == "1-888-555-5555"
