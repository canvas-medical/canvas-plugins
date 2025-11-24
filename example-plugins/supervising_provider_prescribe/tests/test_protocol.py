"""Comprehensive tests for supervising_provider_prescribe plugin."""

from unittest.mock import MagicMock, patch

from pytest import MonkeyPatch

from canvas_sdk.events import EventType


class TestSupervisingProviderPrescribeProtocol:
    """Test suite for supervising_provider_prescribe Protocol."""

    def test_responds_to_correct_event(self) -> None:
        """Test that Protocol responds to PRESCRIBE_COMMAND__POST_ORIGINATE event."""
        from supervising_provider_prescribe.protocols.my_protocol import Protocol

        assert EventType.Name(EventType.PRESCRIBE_COMMAND__POST_ORIGINATE) == Protocol.RESPONDS_TO

    def test_compute_with_staff_available(self, monkeypatch: MonkeyPatch) -> None:
        """Test that compute creates edit effect when staff is available."""
        from supervising_provider_prescribe.protocols.my_protocol import Protocol

        # Mock event and target
        mock_event = MagicMock()
        mock_event.target.id = "test-command-uuid"

        # Mock context
        dummy_context = {"patient": {"id": "test-patient-id"}}

        # Mock staff
        mock_staff = MagicMock()
        mock_staff.id = "test-staff-id"

        # Create protocol instance
        protocol = Protocol(event=mock_event)
        monkeypatch.setattr(type(protocol), "context", property(lambda self: dummy_context))

        # Mock Staff.objects.first()
        with patch(
            "supervising_provider_prescribe.protocols.my_protocol.Staff.objects.first"
        ) as mock_staff_first:
            mock_staff_first.return_value = mock_staff

            # Mock PrescribeCommand
            with patch(
                "supervising_provider_prescribe.protocols.my_protocol.PrescribeCommand"
            ) as mock_command_class:
                mock_command_instance = MagicMock()
                mock_edit_effect = MagicMock()
                mock_command_instance.edit.return_value = mock_edit_effect
                mock_command_class.return_value = mock_command_instance

                result = protocol.compute()

                # Verify PrescribeCommand was created with correct parameters
                mock_command_class.assert_called_once_with(
                    command_uuid="test-command-uuid",
                    supervising_provider_id="test-staff-id",
                )

                # Verify edit() was called
                mock_command_instance.edit.assert_called_once()

                # Verify result
                assert result == [mock_edit_effect]

    def test_compute_without_staff_available(self, monkeypatch: MonkeyPatch) -> None:
        """Test that compute returns empty list when no staff is available."""
        from supervising_provider_prescribe.protocols.my_protocol import Protocol

        # Mock event and target
        mock_event = MagicMock()
        mock_event.target.id = "test-command-uuid"

        # Mock context
        dummy_context = {"patient": {"id": "test-patient-id"}}

        # Create protocol instance
        protocol = Protocol(event=mock_event)
        monkeypatch.setattr(type(protocol), "context", property(lambda self: dummy_context))

        # Mock Staff.objects.first() to return None
        with patch(
            "supervising_provider_prescribe.protocols.my_protocol.Staff.objects.first"
        ) as mock_staff_first:
            mock_staff_first.return_value = None

            result = protocol.compute()

            # Should return empty list when no staff found
            assert result == []

    def test_compute_uses_target_as_command_uuid(self, monkeypatch: MonkeyPatch) -> None:
        """Test that compute correctly uses the target as command_uuid."""
        from supervising_provider_prescribe.protocols.my_protocol import Protocol

        # Mock event with specific target
        mock_event = MagicMock()
        test_uuid = "specific-uuid-12345"
        mock_event.target.id = test_uuid

        # Mock context
        dummy_context = {"patient": {"id": "test-patient-id"}}

        # Mock staff
        mock_staff = MagicMock()
        mock_staff.id = "test-staff-id"

        # Create protocol instance
        protocol = Protocol(event=mock_event)
        monkeypatch.setattr(type(protocol), "context", property(lambda self: dummy_context))

        with patch(
            "supervising_provider_prescribe.protocols.my_protocol.Staff.objects.first"
        ) as mock_staff_first:
            mock_staff_first.return_value = mock_staff

            with patch(
                "supervising_provider_prescribe.protocols.my_protocol.PrescribeCommand"
            ) as mock_command_class:
                mock_command_instance = MagicMock()
                mock_command_class.return_value = mock_command_instance

                protocol.compute()

                # Verify command_uuid is set to the target value
                mock_command_class.assert_called_once()
                call_args = mock_command_class.call_args
                assert call_args[1]["command_uuid"] == test_uuid
