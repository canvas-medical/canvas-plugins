"""Tests for supervising_provider_plugin.protocols.my_protocol module."""

import json
from unittest.mock import MagicMock, patch

from supervising_provider_plugin.protocols.my_protocol import Protocol


class TestProtocol:
    """Tests for Protocol class."""

    def test_responds_to_configuration(self):
        """Test that protocol responds to the correct event types."""
        from canvas_sdk.events import EventType

        expected_events = [
            EventType.Name(EventType.PRESCRIBE__SUPERVISING_PROVIDER__POST_SEARCH),
            EventType.Name(EventType.PRESCRIBE__SUPERVISING_PROVIDER__PRE_SEARCH),
            EventType.Name(EventType.REFILL__SUPERVISING_PROVIDER__POST_SEARCH),
            EventType.Name(EventType.REFILL__SUPERVISING_PROVIDER__PRE_SEARCH),
            EventType.Name(EventType.ADJUST_PRESCRIPTION__SUPERVISING_PROVIDER__POST_SEARCH),
            EventType.Name(EventType.ADJUST_PRESCRIPTION__SUPERVISING_PROVIDER__PRE_SEARCH),
        ]

        assert Protocol.RESPONDS_TO == expected_events

    def test_inherits_from_base_protocol(self):
        """Test that Protocol inherits from BaseProtocol."""
        from canvas_sdk.protocols import BaseProtocol

        assert issubclass(Protocol, BaseProtocol)

    def test_narrative_string(self):
        """Test that narrative string is set correctly."""
        assert (
            Protocol.NARRATIVE_STRING
            == "I was inserted from my supervising provider plugin's protocol."
        )

    def test_compute_no_results_returns_none_payload(self, monkeypatch):
        """Test that compute returns None payload when no results."""
        mock_event = MagicMock()
        protocol = Protocol(event=mock_event)

        mock_context = {"results": None}
        monkeypatch.setattr(type(protocol), "context", property(lambda self: mock_context))

        result = protocol.compute()

        assert len(result) == 1
        payload = json.loads(result[0].payload)
        assert payload is None

    def test_compute_adds_spi_annotations(self, monkeypatch):
        """Test that compute adds SPI number annotations to staff with SPI numbers."""
        mock_event = MagicMock()
        protocol = Protocol(event=mock_event)

        results = [
            {"value": "staff-1", "label": "Dr. Smith"},
            {"value": "staff-2", "label": "Dr. Jones"},
        ]
        mock_context = {"results": results}
        monkeypatch.setattr(type(protocol), "context", property(lambda self: mock_context))

        with patch("supervising_provider_plugin.protocols.my_protocol.Staff.objects.get") as mock_get:
            # Mock staff with and without SPI numbers
            mock_staff_1 = MagicMock()
            mock_staff_1.spi_number = "SPI123"

            mock_staff_2 = MagicMock()
            mock_staff_2.spi_number = None

            def get_staff(dbid):
                if dbid == "staff-1":
                    return mock_staff_1
                return mock_staff_2

            mock_get.side_effect = get_staff

            result = protocol.compute()

            assert len(result) == 1
            payload = json.loads(result[0].payload)

            # First staff should have SPI annotation
            assert "annotations" in payload[0]
            assert payload[0]["annotations"] == ["SPI: SPI123"]

            # Second staff should not have annotations
            assert "annotations" not in payload[1]

    def test_compute_preserves_existing_result_fields(self, monkeypatch):
        """Test that compute preserves all existing fields in results."""
        mock_event = MagicMock()
        protocol = Protocol(event=mock_event)

        results = [
            {
                "value": "staff-1",
                "label": "Dr. Smith",
                "extra_field": "extra_data",
            },
        ]
        mock_context = {"results": results}
        monkeypatch.setattr(type(protocol), "context", property(lambda self: mock_context))

        with patch("supervising_provider_plugin.protocols.my_protocol.Staff.objects.get") as mock_get:
            mock_staff = MagicMock()
            mock_staff.spi_number = "SPI123"
            mock_get.return_value = mock_staff

            result = protocol.compute()

            payload = json.loads(result[0].payload)

            # All original fields should be preserved
            assert payload[0]["value"] == "staff-1"
            assert payload[0]["label"] == "Dr. Smith"
            assert payload[0]["extra_field"] == "extra_data"
            assert payload[0]["annotations"] == ["SPI: SPI123"]
