from unittest.mock import Mock, patch

from canvas_sdk.commands import ImagingOrderCommand
from canvas_sdk.events import EventType

from example_commands.protocols.example_imaging_order import AutoPopulateImagingOrderCommand


def test_imaging_order_protocol_configuration() -> None:
    """Test that the imaging order protocol is configured to respond to the correct event type."""
    assert EventType.Name(EventType.IMAGING_ORDER_COMMAND__POST_ORIGINATE) in AutoPopulateImagingOrderCommand.RESPONDS_TO


def test_imaging_order_protocol_imports() -> None:
    """Test that the imaging order protocol can be imported and has expected attributes."""
    assert AutoPopulateImagingOrderCommand is not None
    assert hasattr(AutoPopulateImagingOrderCommand, "RESPONDS_TO")
    assert hasattr(AutoPopulateImagingOrderCommand, "compute")


def test_imaging_order_protocol_compute_returns_effects() -> None:
    """Test that the imaging order protocol compute method returns effects."""
    # Create a mock event with target UUID
    mock_event = Mock()
    mock_event.target = Mock()
    mock_event.target.id = "test-imaging-order-uuid-123"

    # Instantiate the protocol with the mock event
    protocol = AutoPopulateImagingOrderCommand(event=mock_event)

    # Mock ImagingOrderCommand
    with patch("example_commands.protocols.example_imaging_order.ImagingOrderCommand") as mock_command_class:
        mock_command_instance = Mock()
        mock_command_instance.edit.return_value = Mock()
        mock_command_class.return_value = mock_command_instance

        # Preserve the real Priority enum
        mock_command_class.Priority = ImagingOrderCommand.Priority

        # Call compute and get the effects
        with patch("example_commands.protocols.example_imaging_order.log"):
            effects = protocol.compute()

    # Assert that effects were returned
    assert len(effects) == 1
    assert effects[0] is not None


def test_imaging_order_protocol_populates_required_fields() -> None:
    """Test that the imaging order protocol populates all required fields."""
    # Create a mock event with target UUID
    mock_event = Mock()
    mock_event.target = Mock()
    mock_event.target.id = "test-imaging-order-uuid-456"

    # Instantiate the protocol
    protocol = AutoPopulateImagingOrderCommand(event=mock_event)

    # Mock the ImagingOrderCommand to capture what's being set
    with patch("example_commands.protocols.example_imaging_order.ImagingOrderCommand") as mock_command_class:
        mock_command_instance = Mock()
        mock_edit_effect = Mock()
        mock_command_instance.edit.return_value = mock_edit_effect
        mock_command_class.return_value = mock_command_instance

        # Preserve the real Priority enum
        mock_command_class.Priority = ImagingOrderCommand.Priority

        with patch("example_commands.protocols.example_imaging_order.log"):
            effects = protocol.compute()

        # Verify ImagingOrderCommand was called with correct parameters
        mock_command_class.assert_called_once()
        call_kwargs = mock_command_class.call_args[1]

        assert call_kwargs["command_uuid"] == "test-imaging-order-uuid-456"
        assert call_kwargs["image_code"] == "G0204"
        assert call_kwargs["diagnosis_codes"] == ["E119"]
        assert call_kwargs["priority"] in [
            ImagingOrderCommand.Priority.ROUTINE,
            ImagingOrderCommand.Priority.URGENT,
            ImagingOrderCommand.Priority.STAT,
            None
        ]
        assert call_kwargs["additional_details"] == "Auto-populated imaging order details"
        assert call_kwargs["comment"] == "Example comment for imaging order"
        assert call_kwargs["service_provider"] is not None

        # Verify edit() was called
        mock_command_instance.edit.assert_called_once()


def test_imaging_order_protocol_populates_service_provider() -> None:
    """Test that the imaging order protocol populates service provider information."""
    # Create a mock event
    mock_event = Mock()
    mock_event.target = Mock()
    mock_event.target.id = "test-uuid"

    protocol = AutoPopulateImagingOrderCommand(event=mock_event)

    # Mock to capture service provider
    with patch("example_commands.protocols.example_imaging_order.ImagingOrderCommand") as mock_command_class:
        mock_command_instance = Mock()
        mock_command_instance.edit.return_value = Mock()
        mock_command_class.return_value = mock_command_instance

        # Preserve the real Priority enum
        mock_command_class.Priority = ImagingOrderCommand.Priority

        with patch("example_commands.protocols.example_imaging_order.log"):
            protocol.compute()

        call_kwargs = mock_command_class.call_args[1]
        service_provider = call_kwargs["service_provider"]

        # Verify service provider fields
        assert service_provider.first_name == "Clinic"
        assert service_provider.last_name == "Imaging"
        assert service_provider.practice_name == "Clinic Imaging"
        assert service_provider.specialty == "Radiology"
        assert service_provider.business_address == "123 Imaging St"
        assert service_provider.business_phone == "1234569874"
        assert service_provider.business_fax == "1234569874"
