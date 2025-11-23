from unittest.mock import Mock, patch

from canvas_sdk.commands.commands.refer import ReferCommand
from canvas_sdk.events import EventType

from example_commands.protocols.example_refer import AutoPopulateReferCommand


def test_refer_protocol_configuration() -> None:
    """Test that the refer protocol is configured to respond to the correct event type."""
    assert EventType.Name(EventType.REFER_COMMAND__POST_ORIGINATE) in AutoPopulateReferCommand.RESPONDS_TO


def test_refer_protocol_imports() -> None:
    """Test that the refer protocol can be imported and has expected attributes."""
    assert AutoPopulateReferCommand is not None
    assert hasattr(AutoPopulateReferCommand, "RESPONDS_TO")
    assert hasattr(AutoPopulateReferCommand, "compute")


def test_refer_protocol_compute_returns_effects() -> None:
    """Test that the refer protocol compute method returns effects."""
    # Create a mock event with target UUID
    mock_event = Mock()
    mock_event.target = Mock()
    mock_event.target.id = "test-refer-uuid-123"

    # Instantiate the protocol with the mock event
    protocol = AutoPopulateReferCommand(event=mock_event)

    with patch("example_commands.protocols.example_refer.ReferCommand") as mock_command_class:
        mock_command_instance = Mock()
        mock_command_instance.edit.return_value = Mock()
        mock_command_class.return_value = mock_command_instance

        # Preserve the real enum classes
        mock_command_class.Priority = ReferCommand.Priority
        mock_command_class.ClinicalQuestion = ReferCommand.ClinicalQuestion

        # Call compute and get the effects
        with patch("example_commands.protocols.example_refer.log"):
            effects = protocol.compute()

    # Assert that effects were returned
    assert len(effects) == 1
    assert effects[0] is not None


def test_refer_protocol_populates_required_fields() -> None:
    """Test that the refer protocol populates all required fields."""
    # Create a mock event with target UUID
    mock_event = Mock()
    mock_event.target = Mock()
    mock_event.target.id = "test-refer-uuid-789"

    # Instantiate the protocol
    protocol = AutoPopulateReferCommand(event=mock_event)

    # Mock the ReferCommand to capture what's being set
    with patch("example_commands.protocols.example_refer.ReferCommand") as mock_command_class:
        mock_command_instance = Mock()
        mock_edit_effect = Mock()
        mock_command_instance.edit.return_value = mock_edit_effect
        mock_command_class.return_value = mock_command_instance

        # Preserve the real enum classes
        mock_command_class.Priority = ReferCommand.Priority
        mock_command_class.ClinicalQuestion = ReferCommand.ClinicalQuestion

        with patch("example_commands.protocols.example_refer.log"):
            effects = protocol.compute()

        # Verify ReferCommand was called with correct parameters
        mock_command_class.assert_called_once()
        call_kwargs = mock_command_class.call_args[1]

        assert call_kwargs["command_uuid"] == "test-refer-uuid-789"
        assert call_kwargs["diagnosis_codes"] == ["E119"]
        assert call_kwargs["priority"] in [
            ReferCommand.Priority.URGENT,
            ReferCommand.Priority.ROUTINE,
            ReferCommand.Priority.STAT,
            None
        ]
        assert call_kwargs["clinical_question"] == ReferCommand.ClinicalQuestion.DIAGNOSTIC_UNCERTAINTY
        assert call_kwargs["comment"] == "this is a comment"
        assert call_kwargs["notes_to_specialist"] == "This is a note to specialist"
        assert call_kwargs["include_visit_note"] is True
        assert call_kwargs["service_provider"] is not None

        # Verify edit() was called
        mock_command_instance.edit.assert_called_once()


def test_refer_protocol_populates_service_provider() -> None:
    """Test that the refer protocol populates service provider information."""
    # Create a mock event
    mock_event = Mock()
    mock_event.target = Mock()
    mock_event.target.id = "test-uuid"

    protocol = AutoPopulateReferCommand(event=mock_event)

    # Mock to capture service provider
    with patch("example_commands.protocols.example_refer.ReferCommand") as mock_command_class:
        mock_command_instance = Mock()
        mock_command_instance.edit.return_value = Mock()
        mock_command_class.return_value = mock_command_instance

        # Preserve the real enum classes
        mock_command_class.Priority = ReferCommand.Priority
        mock_command_class.ClinicalQuestion = ReferCommand.ClinicalQuestion

        with patch("example_commands.protocols.example_refer.log"):
            protocol.compute()

        call_kwargs = mock_command_class.call_args[1]
        service_provider = call_kwargs["service_provider"]

        # Verify service provider fields
        assert service_provider.first_name == "Clinic"
        assert service_provider.last_name == "Acupuncture"
        assert service_provider.practice_name == "Clinic Acupuncture"
        assert service_provider.specialty == "Acupuncture"
        assert service_provider.business_address == "Street Address"
        assert service_provider.business_phone == "1234569874"
        assert service_provider.business_fax == "1234569874"


def test_refer_protocol_logs_information() -> None:
    """Test that the refer protocol logs appropriate information."""
    # Create a mock event
    mock_event = Mock()
    mock_event.target = Mock()
    mock_event.target.id = "test-refer-uuid-log"

    protocol = AutoPopulateReferCommand(event=mock_event)

    # Mock ReferCommand and log
    with patch("example_commands.protocols.example_refer.ReferCommand") as mock_command_class:
        mock_command_instance = Mock()
        mock_command_instance.edit.return_value = Mock()
        mock_command_class.return_value = mock_command_instance

        # Preserve the real enum classes
        mock_command_class.Priority = ReferCommand.Priority
        mock_command_class.ClinicalQuestion = ReferCommand.ClinicalQuestion

        with patch("example_commands.protocols.example_refer.log") as mock_log:
            protocol.compute()

            # Verify log.info was called
            mock_log.info.assert_called_once()
            log_message = mock_log.info.call_args[0][0]
            assert "test-refer-uuid-log" in log_message
            assert "refer command" in log_message.lower()
