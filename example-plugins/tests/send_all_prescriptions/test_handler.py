from unittest.mock import MagicMock, patch

import pytest

from send_all_prescriptions.handlers.handler import SendPrescriptionButtonHandler


def test_send_prescription_button_configuration():
    """Test that the SendPrescriptionButtonHandler has the correct configuration."""
    assert SendPrescriptionButtonHandler.BUTTON_TITLE == "Send Prescriptions"
    assert SendPrescriptionButtonHandler.BUTTON_KEY == "SEND_ALL_PRESCRIPTIONS"
    assert (
        SendPrescriptionButtonHandler.BUTTON_LOCATION
        == SendPrescriptionButtonHandler.ButtonLocation.NOTE_FOOTER
    )


@pytest.mark.django_db
def test_send_prescription_button_handle_no_prescriptions(monkeypatch):
    """Test that handle() returns empty list when there are no prescriptions."""
    # Create handler instance with mocked event
    dummy_context = {"note_id": "test-note-id"}
    handler = SendPrescriptionButtonHandler(event=MagicMock())
    monkeypatch.setattr(type(handler), "context", property(lambda self: dummy_context))

    # Mock the Command query to return no prescriptions
    with patch("send_all_prescriptions.handlers.handler.Command.objects.filter") as mock_filter:
        mock_filter.return_value = []

        # Call the handle method
        effects = handler.handle()

    # Should return empty list
    assert effects == []


@pytest.mark.django_db
def test_send_prescription_button_handle_with_prescriptions(monkeypatch):
    """Test that handle() creates send effects for all committed prescriptions."""
    # Create handler instance with mocked event
    dummy_context = {"note_id": "test-note-id"}
    handler = SendPrescriptionButtonHandler(event=MagicMock())
    monkeypatch.setattr(type(handler), "context", property(lambda self: dummy_context))

    # Create mock commands
    mock_command1 = MagicMock()
    mock_command1.id = "command-1"
    mock_command2 = MagicMock()
    mock_command2.id = "command-2"

    # Mock the Command query to return prescriptions
    with patch("send_all_prescriptions.handlers.handler.Command.objects.filter") as mock_filter:
        mock_filter.return_value = [mock_command1, mock_command2]

        with patch("send_all_prescriptions.handlers.handler.PrescribeCommand") as mock_prescribe:
            # Mock the PrescribeCommand instances
            mock_prescribe_instance1 = MagicMock()
            mock_prescribe_instance1.send.return_value = MagicMock()

            mock_prescribe_instance2 = MagicMock()
            mock_prescribe_instance2.send.return_value = MagicMock()

            mock_prescribe.side_effect = [mock_prescribe_instance1, mock_prescribe_instance2]

            # Call the handle method
            effects = handler.handle()

    # Should return 2 effects
    assert len(effects) == 2

    # Verify the command UUIDs were set correctly
    assert mock_prescribe_instance1.command_uuid == "command-1"
    assert mock_prescribe_instance2.command_uuid == "command-2"

    # Verify send() was called on both
    mock_prescribe_instance1.send.assert_called_once()
    mock_prescribe_instance2.send.assert_called_once()


@pytest.mark.django_db
def test_send_prescription_button_handle_no_note_id(monkeypatch):
    """Test that handle() works when note_id is not in context."""
    # Create handler instance with mocked event
    dummy_context = {}
    handler = SendPrescriptionButtonHandler(event=MagicMock())
    monkeypatch.setattr(type(handler), "context", property(lambda self: dummy_context))

    # Mock the Command query
    with patch("send_all_prescriptions.handlers.handler.Command.objects.filter") as mock_filter:
        mock_filter.return_value = []

        # Call the handle method
        effects = handler.handle()

    # Should call filter with None for note_id
    mock_filter.assert_called_once_with(
        note_id=None, schema_key="prescribe", committer__isnull=False
    )

    # Should return empty list
    assert effects == []
