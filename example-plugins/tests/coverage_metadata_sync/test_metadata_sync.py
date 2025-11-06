from unittest.mock import MagicMock, patch

import pytest

from coverage_metadata_sync.protocols.metadata_sync import CoverageStatusSyncProtocol

from canvas_sdk.events import EventType


class TestCoverageStatusSyncProtocol:
    """Tests for the CoverageStatusSyncProtocol."""

    def test_compute_label_added_missing_coverage(self, monkeypatch):
        """Test that adding MISSING_COVERAGE label sets coverage_status to 'Missing'."""
        # Create protocol instance
        protocol = CoverageStatusSyncProtocol(event=MagicMock())
        protocol.event.type = EventType.APPOINTMENT_LABEL_ADDED

        # Set up context
        dummy_context = {
            "patient": {"id": "patient-123"},
            "label": "MISSING_COVERAGE",
        }
        monkeypatch.setattr(type(protocol), "context", property(lambda self: dummy_context))

        # Mock PatientMetadata
        with patch(
            "coverage_metadata_sync.protocols.metadata_sync.PatientMetadata"
        ) as mock_metadata_class:
            mock_metadata_instance = MagicMock()
            mock_upsert_effect = MagicMock()
            mock_metadata_instance.upsert.return_value = mock_upsert_effect
            mock_metadata_class.return_value = mock_metadata_instance

            with patch("coverage_metadata_sync.protocols.metadata_sync.log"):
                # Call compute
                effects = protocol.compute()

            # Verify PatientMetadata was created correctly
            mock_metadata_class.assert_called_once_with(
                patient_id="patient-123", key="coverage_status"
            )

            # Verify upsert was called with "Missing"
            mock_metadata_instance.upsert.assert_called_once_with(value="Missing")

            # Verify result
            assert len(effects) == 1
            assert effects[0] == mock_upsert_effect

    def test_compute_label_removed_missing_coverage(self, monkeypatch):
        """Test that removing MISSING_COVERAGE label sets coverage_status to 'Active'."""
        # Create protocol instance
        protocol = CoverageStatusSyncProtocol(event=MagicMock())
        protocol.event.type = EventType.APPOINTMENT_LABEL_REMOVED

        # Set up context
        dummy_context = {
            "patient": {"id": "patient-123"},
            "label": "MISSING_COVERAGE",
        }
        monkeypatch.setattr(type(protocol), "context", property(lambda self: dummy_context))

        # Mock PatientMetadata
        with patch(
            "coverage_metadata_sync.protocols.metadata_sync.PatientMetadata"
        ) as mock_metadata_class:
            mock_metadata_instance = MagicMock()
            mock_upsert_effect = MagicMock()
            mock_metadata_instance.upsert.return_value = mock_upsert_effect
            mock_metadata_class.return_value = mock_metadata_instance

            with patch("coverage_metadata_sync.protocols.metadata_sync.log"):
                # Call compute
                effects = protocol.compute()

            # Verify upsert was called with "Active"
            mock_metadata_instance.upsert.assert_called_once_with(value="Active")

            # Verify result
            assert len(effects) == 1
            assert effects[0] == mock_upsert_effect

    def test_compute_ignores_other_labels(self, monkeypatch):
        """Test that events for other labels are ignored."""
        # Create protocol instance
        protocol = CoverageStatusSyncProtocol(event=MagicMock())
        protocol.event.type = EventType.APPOINTMENT_LABEL_ADDED

        # Set up context with a different label
        dummy_context = {
            "patient": {"id": "patient-123"},
            "label": "SOME_OTHER_LABEL",
        }
        monkeypatch.setattr(type(protocol), "context", property(lambda self: dummy_context))

        with patch("coverage_metadata_sync.protocols.metadata_sync.log"):
            # Call compute
            effects = protocol.compute()

        # Should return empty list
        assert effects == []

    def test_compute_no_patient_id(self, monkeypatch):
        """Test that missing patient ID returns empty list."""
        # Create protocol instance
        protocol = CoverageStatusSyncProtocol(event=MagicMock())
        protocol.event.type = EventType.APPOINTMENT_LABEL_ADDED

        # Set up context without patient ID
        dummy_context = {
            "patient": {},
            "label": "MISSING_COVERAGE",
        }
        monkeypatch.setattr(type(protocol), "context", property(lambda self: dummy_context))

        with patch("coverage_metadata_sync.protocols.metadata_sync.log"):
            # Call compute
            effects = protocol.compute()

        # Should return empty list
        assert effects == []

    def test_compute_no_label(self, monkeypatch):
        """Test that missing label returns empty list."""
        # Create protocol instance
        protocol = CoverageStatusSyncProtocol(event=MagicMock())
        protocol.event.type = EventType.APPOINTMENT_LABEL_ADDED

        # Set up context without label
        dummy_context = {
            "patient": {"id": "patient-123"},
        }
        monkeypatch.setattr(type(protocol), "context", property(lambda self: dummy_context))

        with patch("coverage_metadata_sync.protocols.metadata_sync.log"):
            # Call compute
            effects = protocol.compute()

        # Should return empty list
        assert effects == []

    def test_compute_handles_exception(self, monkeypatch):
        """Test that exceptions during metadata creation are handled gracefully."""
        # Create protocol instance
        protocol = CoverageStatusSyncProtocol(event=MagicMock())
        protocol.event.type = EventType.APPOINTMENT_LABEL_ADDED

        # Set up context
        dummy_context = {
            "patient": {"id": "patient-123"},
            "label": "MISSING_COVERAGE",
        }
        monkeypatch.setattr(type(protocol), "context", property(lambda self: dummy_context))

        # Mock PatientMetadata to raise exception
        with patch(
            "coverage_metadata_sync.protocols.metadata_sync.PatientMetadata"
        ) as mock_metadata_class:
            mock_metadata_class.side_effect = Exception("Test error")

            with patch("coverage_metadata_sync.protocols.metadata_sync.log"):
                # Call compute
                effects = protocol.compute()

        # Should return empty list when exception occurs
        assert effects == []
