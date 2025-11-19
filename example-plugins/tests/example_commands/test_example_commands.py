# To run the tests, use the command `pytest` in the terminal or uv run pytest.
# Each test is wrapped inside a transaction that is rolled back at the end of the test.
# If you want to modify which files are used for testing, check the [tool.pytest.ini_options] section in pyproject.toml.
# For more information on testing Canvas plugins, see: https://docs.canvasmedical.com/sdk/testing-utils/

from unittest.mock import Mock, patch

import pytest
from canvas_sdk.effects import EffectType
from canvas_sdk.events import EventType
from canvas_sdk.test_utils.factories import PatientFactory
from canvas_sdk.v1.data.discount import Discount

from example_commands.protocols.example_imaging_order import AutoPopulateImagingOrderCommand
from example_commands.protocols.example_refer import AutoPopulateReferCommand


# ============================================================================
# Tests for AutoPopulateImagingOrderCommand Protocol
# ============================================================================


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

    # Mock ImagingOrderCommand to avoid Priority.STAT issue
    with patch("example_commands.protocols.example_imaging_order.ImagingOrderCommand") as mock_command_class:
        mock_command_instance = Mock()
        mock_command_instance.edit.return_value = Mock()
        mock_command_class.return_value = mock_command_instance

        # Mock Priority enum
        # mock_priority = Mock()
        # mock_priority.ROUTINE = "ROUTINE"
        # mock_priority.URGENT = "URGENT"
        # mock_priority.STAT = "STAT"
        # mock_command_class.Priority = mock_priority

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

        # Mock Priority enum
        mock_priority = Mock()
        mock_priority.ROUTINE = "ROUTINE"
        mock_priority.URGENT = "URGENT"
        mock_priority.STAT = "STAT"
        mock_command_class.Priority = mock_priority

        with patch("example_commands.protocols.example_imaging_order.log"):
            effects = protocol.compute()

        # Verify ImagingOrderCommand was called with correct parameters
        mock_command_class.assert_called_once()
        call_kwargs = mock_command_class.call_args[1]

        assert call_kwargs["command_uuid"] == "test-imaging-order-uuid-456"
        assert call_kwargs["image_code"] == "G0204"
        assert call_kwargs["diagnosis_codes"] == ["E119"]
        assert call_kwargs["priority"] in ["ROUTINE", "URGENT", "STAT", None]
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

        # Mock Priority enum
        mock_priority = Mock()
        mock_priority.ROUTINE = "ROUTINE"
        mock_priority.URGENT = "URGENT"
        mock_priority.STAT = "STAT"
        mock_command_class.Priority = mock_priority

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


# ============================================================================
# Tests for AutoPopulateReferCommand Protocol
# ============================================================================


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

    # Mock ReferCommand to avoid Priority.STAT issue
    with patch("example_commands.protocols.example_refer.ReferCommand") as mock_command_class:
        mock_command_instance = Mock()
        mock_command_instance.edit.return_value = Mock()
        mock_command_class.return_value = mock_command_instance

        # Mock Priority enum
        mock_priority = Mock()
        mock_priority.URGENT = "URGENT"
        mock_priority.ROUTINE = "ROUTINE"
        mock_priority.STAT = "STAT"
        mock_command_class.Priority = mock_priority

        # Mock ClinicalQuestion enum
        mock_clinical_question = Mock()
        mock_clinical_question.DIAGNOSTIC_UNCERTAINTY = "DIAGNOSTIC_UNCERTAINTY"
        mock_command_class.ClinicalQuestion = mock_clinical_question

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

        # Mock Priority enum
        mock_priority = Mock()
        mock_priority.URGENT = "URGENT"
        mock_priority.ROUTINE = "ROUTINE"
        mock_priority.STAT = "STAT"
        mock_command_class.Priority = mock_priority

        # Mock ClinicalQuestion enum
        mock_clinical_question = Mock()
        mock_clinical_question.DIAGNOSTIC_UNCERTAINTY = "DIAGNOSTIC_UNCERTAINTY"
        mock_command_class.ClinicalQuestion = mock_clinical_question

        with patch("example_commands.protocols.example_refer.log"):
            effects = protocol.compute()

        # Verify ReferCommand was called with correct parameters
        mock_command_class.assert_called_once()
        call_kwargs = mock_command_class.call_args[1]

        assert call_kwargs["command_uuid"] == "test-refer-uuid-789"
        assert call_kwargs["diagnosis_codes"] == ["E119"]
        assert call_kwargs["priority"] in ["URGENT", "ROUTINE", "STAT", None]
        assert call_kwargs["clinical_question"] == "DIAGNOSTIC_UNCERTAINTY"
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

        # Mock Priority enum
        mock_priority = Mock()
        mock_priority.URGENT = "URGENT"
        mock_priority.ROUTINE = "ROUTINE"
        mock_priority.STAT = "STAT"
        mock_command_class.Priority = mock_priority

        # Mock ClinicalQuestion enum
        mock_clinical_question = Mock()
        mock_clinical_question.DIAGNOSTIC_UNCERTAINTY = "DIAGNOSTIC_UNCERTAINTY"
        mock_command_class.ClinicalQuestion = mock_clinical_question

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

        # Mock Priority enum
        mock_priority = Mock()
        mock_priority.URGENT = "URGENT"
        mock_priority.ROUTINE = "ROUTINE"
        mock_priority.STAT = "STAT"
        mock_command_class.Priority = mock_priority

        # Mock ClinicalQuestion enum
        mock_clinical_question = Mock()
        mock_clinical_question.DIAGNOSTIC_UNCERTAINTY = "DIAGNOSTIC_UNCERTAINTY"
        mock_command_class.ClinicalQuestion = mock_clinical_question

        with patch("example_commands.protocols.example_refer.log") as mock_log:
            protocol.compute()

            # Verify log.info was called
            mock_log.info.assert_called_once()
            log_message = mock_log.info.call_args[0][0]
            assert "test-refer-uuid-log" in log_message
            assert "refer command" in log_message.lower()


# ============================================================================
# General Factory and Model Examples
# ============================================================================


# Example: You can use a factory to create a patient instance for testing purposes.
def test_factory_example() -> None:
    """Test that a patient can be created using the PatientFactory."""
    patient = PatientFactory.create()
    assert patient.id is not None


# Example: If a factory is not available, you can create an instance manually with the data model directly.
def test_model_example() -> None:
    """Test that a Discount instance can be created."""
    Discount.objects.create(name="10%", adjustment_group="30", adjustment_code="CO", discount=0.10)
    assert Discount.objects.first().pk is not None
