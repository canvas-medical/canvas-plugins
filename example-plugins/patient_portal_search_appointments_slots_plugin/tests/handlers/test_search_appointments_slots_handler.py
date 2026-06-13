"""Tests for patient_portal_search_appointments_slots_plugin.handlers.search_appointments_slots_handler module."""

import json
from unittest.mock import MagicMock

from patient_portal_search_appointments_slots_plugin.handlers.search_appointments_slots_handler import (
    SearchAppointmentsSlotsHandler,
)


class TestSearchAppointmentsSlotsHandler:
    """Tests for SearchAppointmentsSlotsHandler class."""

    def test_responds_to_configuration(self):
        """Test that handler responds to the correct event type."""
        from canvas_sdk.events import EventType

        assert SearchAppointmentsSlotsHandler.RESPONDS_TO == EventType.Name(
            EventType.PATIENT_PORTAL__APPOINTMENTS__SLOTS__POST_SEARCH
        )

    def test_inherits_from_base_handler(self):
        """Test that SearchAppointmentsSlotsHandler inherits from BaseHandler."""
        from canvas_sdk.handlers.base import BaseHandler

        assert issubclass(SearchAppointmentsSlotsHandler, BaseHandler)

    def test_compute_no_slots_returns_none_payload(self, monkeypatch):
        """Test that compute returns None payload when no slots provided."""
        mock_event = MagicMock()
        handler = SearchAppointmentsSlotsHandler(event=mock_event)

        mock_context = {"slots_by_provider": "{}"}
        monkeypatch.setattr(type(handler), "context", property(lambda self: mock_context))

        result = handler.compute()

        assert len(result) == 1
        payload = json.loads(result[0].payload)
        assert payload is None

    def test_compute_filters_empty_slots(self, monkeypatch):
        """Test that compute filters out providers with no available slots."""
        mock_event = MagicMock()
        handler = SearchAppointmentsSlotsHandler(event=mock_event)

        slots_data = {
            "provider-1": {"2025-01-01": ["09:00", "10:00"]},
            "provider-2": {"2025-01-01": []},  # No slots
            "provider-3": {"2025-01-01": ["14:00"]},
        }
        mock_context = {"slots_by_provider": json.dumps(slots_data)}
        monkeypatch.setattr(type(handler), "context", property(lambda self: mock_context))

        result = handler.compute()

        assert len(result) == 1
        payload = json.loads(result[0].payload)

        # Only providers with slots should be included
        assert "provider-1" in payload["slots_by_provider"]
        assert "provider-2" not in payload["slots_by_provider"]
        assert "provider-3" in payload["slots_by_provider"]

    def test_respond_with_creates_correct_effect(self):
        """Test that _respond_with creates effect with correct structure."""
        mock_event = MagicMock()
        handler = SearchAppointmentsSlotsHandler(event=mock_event)

        payload = {"test": "data"}
        effect = handler._respond_with(payload)

        from canvas_sdk.effects import EffectType

        assert effect.type == EffectType.PATIENT_PORTAL__APPOINTMENTS__SLOTS__POST_SEARCH_RESULTS
        assert json.loads(effect.payload) == payload

    def test_respond_with_handles_none_payload(self):
        """Test that _respond_with handles None payload correctly."""
        mock_event = MagicMock()
        handler = SearchAppointmentsSlotsHandler(event=mock_event)

        effect = handler._respond_with(None)

        assert json.loads(effect.payload) is None
