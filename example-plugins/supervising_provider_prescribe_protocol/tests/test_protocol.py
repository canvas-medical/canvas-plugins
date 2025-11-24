"""Comprehensive tests for supervising_provider_prescribe_protocol plugin."""

from unittest.mock import MagicMock, patch

from pytest import MonkeyPatch

from canvas_sdk.events import EventType


class TestSupervisingProviderPrescribeProtocolCard:
    """Test suite for supervising_provider_prescribe_protocol Protocol."""

    def test_responds_to_correct_event(self) -> None:
        """Test that Protocol responds to NOTE_STATE_CHANGE_EVENT_CREATED event."""
        from supervising_provider_prescribe_protocol.protocols.my_protocol import Protocol

        assert EventType.Name(EventType.NOTE_STATE_CHANGE_EVENT_CREATED) == Protocol.RESPONDS_TO

    def test_compute_with_staff_available(self, monkeypatch: MonkeyPatch) -> None:
        """Test that compute creates protocol card with prescribe recommendation when staff available."""
        from supervising_provider_prescribe_protocol.protocols.my_protocol import Protocol

        # Mock event
        mock_event = MagicMock()

        # Mock context
        dummy_context = {"patient_id": "test-patient-id", "note_id": "test-note-id"}

        # Mock staff
        mock_staff = MagicMock()
        mock_staff.id = "test-staff-id"

        # Create protocol instance
        protocol = Protocol(event=mock_event)
        monkeypatch.setattr(type(protocol), "context", property(lambda self: dummy_context))

        # Mock Staff.objects.first()
        with patch(
            "supervising_provider_prescribe_protocol.protocols.my_protocol.Staff.objects.first"
        ) as mock_staff_first:
            mock_staff_first.return_value = mock_staff

            # Mock PrescribeCommand
            with patch(
                "supervising_provider_prescribe_protocol.protocols.my_protocol.PrescribeCommand"
            ) as mock_command_class:
                mock_command_instance = MagicMock()
                mock_recommendation = MagicMock()
                mock_command_instance.recommend.return_value = mock_recommendation
                mock_command_class.return_value = mock_command_instance

                # Mock ProtocolCard
                with patch(
                    "supervising_provider_prescribe_protocol.protocols.my_protocol.ProtocolCard"
                ) as mock_card_class:
                    mock_card_instance = MagicMock()
                    mock_card_instance.recommendations = []
                    mock_applied_card = MagicMock()
                    mock_card_instance.apply.return_value = mock_applied_card
                    mock_card_class.return_value = mock_card_instance

                    result = protocol.compute()

                    # Verify ProtocolCard was created with correct parameters
                    mock_card_class.assert_called_once_with(
                        patient_id="test-patient-id",
                        key="test-supervising-provider-prescribe",
                        title="Test Prescribe Command with Supervising Provider",
                    )

                    # Verify PrescribeCommand was created with supervising_provider_id
                    mock_command_class.assert_called_once_with(
                        supervising_provider_id="test-staff-id",
                    )

                    # Verify recommend() was called
                    mock_command_instance.recommend.assert_called_once_with(
                        title="This inserts a prescribe command", button="Prescribe"
                    )

                    # Verify recommendation was appended
                    assert mock_recommendation in mock_card_instance.recommendations

                    # Verify apply() was called
                    mock_card_instance.apply.assert_called_once()

                    # Verify result
                    assert result == [mock_applied_card]

    def test_compute_without_staff_available(self, monkeypatch: MonkeyPatch) -> None:
        """Test that compute returns empty list when no staff is available."""
        from supervising_provider_prescribe_protocol.protocols.my_protocol import Protocol

        # Mock event
        mock_event = MagicMock()

        # Mock context
        dummy_context = {"patient_id": "test-patient-id", "note_id": "test-note-id"}

        # Create protocol instance
        protocol = Protocol(event=mock_event)
        monkeypatch.setattr(type(protocol), "context", property(lambda self: dummy_context))

        # Mock Staff.objects.first() to return None
        with patch(
            "supervising_provider_prescribe_protocol.protocols.my_protocol.Staff.objects.first"
        ) as mock_staff_first:
            mock_staff_first.return_value = None

            result = protocol.compute()

            # Should return empty list when no staff found
            assert result == []

    def test_compute_uses_context_patient_id(self, monkeypatch: MonkeyPatch) -> None:
        """Test that compute uses patient_id from context."""
        from supervising_provider_prescribe_protocol.protocols.my_protocol import Protocol

        # Mock event
        mock_event = MagicMock()

        # Mock context with specific patient_id
        test_patient_id = "specific-patient-id-123"
        dummy_context = {"patient_id": test_patient_id, "note_id": "test-note-id"}

        # Mock staff
        mock_staff = MagicMock()
        mock_staff.id = "test-staff-id"

        # Create protocol instance
        protocol = Protocol(event=mock_event)
        monkeypatch.setattr(type(protocol), "context", property(lambda self: dummy_context))

        with patch(
            "supervising_provider_prescribe_protocol.protocols.my_protocol.Staff.objects.first"
        ) as mock_staff_first:
            mock_staff_first.return_value = mock_staff

            with (
                patch(
                    "supervising_provider_prescribe_protocol.protocols.my_protocol.PrescribeCommand"
                ),
                patch(
                    "supervising_provider_prescribe_protocol.protocols.my_protocol.ProtocolCard"
                ) as mock_card_class,
            ):
                mock_card_instance = MagicMock()
                mock_card_instance.recommendations = []
                mock_card_class.return_value = mock_card_instance

                protocol.compute()

                # Verify ProtocolCard was created with correct patient_id
                mock_card_class.assert_called_once()
                call_args = mock_card_class.call_args
                assert call_args[1]["patient_id"] == test_patient_id
