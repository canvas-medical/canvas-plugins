"""
Tests for appointment reason for visit functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4

from canvas_sdk.v1.data.appointment import Appointment


class TestAppointmentReasonForVisit:
    """Test the new reason for visit methods on the Appointment model."""

    @pytest.fixture
    def appointment(self):
        """Create a test appointment instance."""
        appointment = Appointment()
        appointment.note_id = str(uuid4())
        return appointment

    @pytest.fixture
    def appointment_without_note(self):
        """Create a test appointment without a note."""
        appointment = Appointment()
        appointment.note_id = None
        return appointment

    @pytest.fixture
    def mock_reason_coding(self):
        """Create a mock ReasonForVisitSettingCoding."""
        reason = Mock()
        reason.id = str(uuid4())
        reason.code = "183824009"
        reason.display = "Annual health maintenance visit"
        reason.system = "http://snomed.info/sct"
        return reason

    @pytest.fixture
    def mock_command(self, mock_reason_coding):
        """Create a mock Command with reason for visit data."""
        command = Mock()
        command.id = str(uuid4())
        command.schema_key = "reasonForVisit"
        command.data = {
            "coding": mock_reason_coding.id,
            "structured": True,
            "comment": "Annual physical examination"
        }
        return command

    def test_reason_for_visit_property_with_no_note(self, appointment_without_note):
        """Test reason_for_visit property when appointment has no note."""
        assert appointment_without_note.reason_for_visit is None

    @patch('canvas_sdk.v1.data.appointment.Command')
    def test_get_reasons_for_visit_with_no_note(self, mock_command_class, appointment_without_note):
        """Test get_reasons_for_visit when appointment has no note."""
        result = appointment_without_note.get_reasons_for_visit()
        assert result == []
        # Should not call Command.objects.filter when no note
        mock_command_class.objects.filter.assert_not_called()

    @patch('canvas_sdk.v1.data.appointment.Command')
    def test_get_reason_for_visit_commands_with_no_note(self, mock_command_class, appointment_without_note):
        """Test get_reason_for_visit_commands when appointment has no note."""
        result = appointment_without_note.get_reason_for_visit_commands()
        assert result == []
        # Should not call Command.objects.filter when no note
        mock_command_class.objects.filter.assert_not_called()

    @patch('canvas_sdk.v1.data.appointment.Command')
    @patch('canvas_sdk.v1.data.appointment.ReasonForVisitSettingCoding')
    def test_get_reasons_for_visit_with_string_coding(
        self, mock_reason_class, mock_command_class, appointment, mock_reason_coding, mock_command
    ):
        """Test get_reasons_for_visit with string coding reference."""
        # Setup mocks
        mock_queryset = MagicMock()
        mock_queryset.exclude.return_value = [mock_command]
        mock_command_class.objects.filter.return_value = mock_queryset
        mock_reason_class.objects.get.return_value = mock_reason_coding

        result = appointment.get_reasons_for_visit()

        # Verify the query was made correctly
        mock_command_class.objects.filter.assert_called_once_with(
            note_id=appointment.note_id,
            schema_key="reasonForVisit"
        )
        mock_queryset.exclude.assert_called_once_with(entered_in_error__isnull=False)

        # Verify the reason coding was fetched
        mock_reason_class.objects.get.assert_called_once_with(id=mock_reason_coding.id)

        # Verify the result
        assert len(result) == 1
        assert result[0] == mock_reason_coding

    @patch('canvas_sdk.v1.data.appointment.Command')
    @patch('canvas_sdk.v1.data.appointment.ReasonForVisitSettingCoding')
    def test_get_reasons_for_visit_with_dict_coding(
        self, mock_reason_class, mock_command_class, appointment, mock_reason_coding
    ):
        """Test get_reasons_for_visit with dict coding reference."""
        # Create command with dict coding
        mock_command = Mock()
        mock_command.data = {
            "coding": {
                "code": "183824009",
                "system": "http://snomed.info/sct"
            }
        }

        # Setup mocks
        mock_queryset = MagicMock()
        mock_queryset.exclude.return_value = [mock_command]
        mock_command_class.objects.filter.return_value = mock_queryset
        mock_reason_class.objects.get.return_value = mock_reason_coding

        result = appointment.get_reasons_for_visit()

        # Verify the reason coding was fetched with code and system
        mock_reason_class.objects.get.assert_called_once_with(
            code="183824009",
            system="http://snomed.info/sct"
        )

        # Verify the result
        assert len(result) == 1
        assert result[0] == mock_reason_coding

    @patch('canvas_sdk.v1.data.appointment.Command')
    @patch('canvas_sdk.v1.data.appointment.ReasonForVisitSettingCoding')
    def test_get_reasons_for_visit_handles_missing_coding(
        self, mock_reason_class, mock_command_class, appointment
    ):
        """Test get_reasons_for_visit handles missing reason coding gracefully."""
        # Create command with invalid coding reference
        mock_command = Mock()
        mock_command.data = {"coding": "invalid-id"}

        # Setup mocks
        mock_queryset = MagicMock()
        mock_queryset.exclude.return_value = [mock_command]
        mock_command_class.objects.filter.return_value = mock_queryset
        
        # Make the reason coding lookup fail
        from canvas_sdk.v1.data.reason_for_visit import ReasonForVisitSettingCoding
        mock_reason_class.objects.get.side_effect = ReasonForVisitSettingCoding.DoesNotExist()

        result = appointment.get_reasons_for_visit()

        # Should return empty list, not raise exception
        assert result == []

    @patch('canvas_sdk.v1.data.appointment.Command')
    def test_get_reason_for_visit_commands(self, mock_command_class, appointment, mock_command):
        """Test get_reason_for_visit_commands returns command objects."""
        # Setup mocks
        mock_queryset = MagicMock()
        mock_queryset.exclude.return_value = [mock_command]
        mock_command_class.objects.filter.return_value = mock_queryset

        result = appointment.get_reason_for_visit_commands()

        # Verify the query was made correctly
        mock_command_class.objects.filter.assert_called_once_with(
            note_id=appointment.note_id,
            schema_key="reasonForVisit"
        )
        mock_queryset.exclude.assert_called_once_with(entered_in_error__isnull=False)

        # Verify the result
        assert len(result) == 1
        assert result[0] == mock_command

    @patch('canvas_sdk.v1.data.appointment.Command')
    @patch('canvas_sdk.v1.data.appointment.ReasonForVisitSettingCoding')
    def test_reason_for_visit_property_returns_first_reason(
        self, mock_reason_class, mock_command_class, appointment, mock_reason_coding
    ):
        """Test reason_for_visit property returns the first reason."""
        # Create multiple commands
        mock_command1 = Mock()
        mock_command1.data = {"coding": "reason-1"}
        mock_command2 = Mock()
        mock_command2.data = {"coding": "reason-2"}

        # Setup mocks
        mock_queryset = MagicMock()
        mock_queryset.exclude.return_value = [mock_command1, mock_command2]
        mock_command_class.objects.filter.return_value = mock_queryset
        mock_reason_class.objects.get.return_value = mock_reason_coding

        result = appointment.reason_for_visit

        # Should return the first reason only
        assert result == mock_reason_coding

    @patch('canvas_sdk.v1.data.appointment.Command')
    def test_reason_for_visit_property_returns_none_when_no_reasons(
        self, mock_command_class, appointment
    ):
        """Test reason_for_visit property returns None when no reasons found."""
        # Setup mocks to return empty list
        mock_queryset = MagicMock()
        mock_queryset.exclude.return_value = []
        mock_command_class.objects.filter.return_value = mock_queryset

        result = appointment.reason_for_visit

        assert result is None

    def test_methods_exist_on_appointment_class(self):
        """Test that the new methods exist on the Appointment class."""
        appointment = Appointment()
        
        # Check that the methods exist
        assert hasattr(appointment, 'reason_for_visit')
        assert hasattr(appointment, 'get_reasons_for_visit')
        assert hasattr(appointment, 'get_reason_for_visit_commands')
        
        # Check that they are callable (except the property)
        assert callable(appointment.get_reasons_for_visit)
        assert callable(appointment.get_reason_for_visit_commands)