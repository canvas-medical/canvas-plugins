"""Tests for recurring_appointments.handlers.recurrence module."""

import datetime
from unittest.mock import MagicMock, patch

import pytest

from recurring_appointments.handlers.recurrence import AppointmentRecurrence
from recurring_appointments.utils.constants import (
    RecurrenceEnum,
    FIELD_RECURRENCE_TYPE_KEY,
    FIELD_RECURRENCE_INTERVAL_KEY,
    FIELD_RECURRENCE_STOP_AFTER_KEY,
)


@pytest.fixture
def handler():
    """Create an AppointmentRecurrence handler with mocked event."""
    mock_event = MagicMock()
    mock_event.target.id = "appointment-123"
    mock_event.context = {"patient": {"id": "patient-123"}}
    return AppointmentRecurrence(event=mock_event)


@pytest.fixture
def mock_appointment():
    """Create a mock appointment."""
    appointment = MagicMock()
    appointment.id = "appointment-123"
    appointment.start_time = datetime.datetime(2025, 1, 15, 10, 0, 0)
    appointment.duration_minutes = 30
    appointment.provider.id = "provider-123"
    appointment.location.id = "location-123"
    appointment.meeting_link = "https://example.com/meeting"
    appointment.note_type.id = "note-type-123"
    appointment.description = "Test appointment"
    return appointment


class TestAppointmentRecurrence:
    """Tests for AppointmentRecurrence handler."""

    def test_responds_to_configuration(self):
        """Test that handler responds to the correct event type."""
        from canvas_sdk.events import EventType

        assert AppointmentRecurrence.RESPONDS_TO == EventType.Name(
            EventType.APPOINTMENT_CREATED
        )

    def test_inherits_from_base_handler(self):
        """Test that AppointmentRecurrence inherits from BaseHandler."""
        from canvas_sdk.handlers.base import BaseHandler

        assert issubclass(AppointmentRecurrence, BaseHandler)

    def test_appointment_property(self, handler):
        """Test that appointment property fetches and caches the appointment."""
        with patch(
            "recurring_appointments.handlers.recurrence.AppointmentModel.objects.get"
        ) as mock_get:
            mock_appt = MagicMock()
            mock_get.return_value = mock_appt

            # First call should fetch
            result1 = handler.appointment
            assert result1 == mock_appt
            mock_get.assert_called_once_with(id="appointment-123")

            # Second call should use cached value
            result2 = handler.appointment
            assert result2 == mock_appt
            assert mock_get.call_count == 1  # Still only called once

    def test_recurrence_type_property_with_metadata(self, handler, mock_appointment):
        """Test recurrence_type property when metadata exists."""
        handler._appointment = mock_appointment

        with patch(
            "recurring_appointments.handlers.recurrence.AppointmentMetadata.objects.filter"
        ) as mock_filter:
            mock_queryset = MagicMock()
            mock_queryset.values_list.return_value.first.return_value = "Week(s)"
            mock_filter.return_value = mock_queryset

            result = handler.recurrence_type

            assert result == "Week(s)"
            mock_filter.assert_called_once_with(
                appointment=mock_appointment, key=FIELD_RECURRENCE_TYPE_KEY
            )

    def test_recurrence_type_property_without_metadata(self, handler, mock_appointment):
        """Test recurrence_type property when no metadata exists."""
        handler._appointment = mock_appointment

        with patch(
            "recurring_appointments.handlers.recurrence.AppointmentMetadata.objects.filter"
        ) as mock_filter:
            mock_queryset = MagicMock()
            mock_queryset.values_list.return_value.first.return_value = None
            mock_filter.return_value = mock_queryset

            result = handler.recurrence_type

            assert result == RecurrenceEnum.NONE.value

    def test_recurrence_interval_property_with_valid_metadata(self, handler, mock_appointment):
        """Test recurrence_interval property with valid metadata."""
        handler._appointment = mock_appointment

        with patch(
            "recurring_appointments.handlers.recurrence.AppointmentMetadata.objects.filter"
        ) as mock_filter:
            mock_queryset = MagicMock()
            mock_queryset.values_list.return_value.first.return_value = "5"
            mock_filter.return_value = mock_queryset

            result = handler.recurrence_interval

            assert result == 5
            mock_filter.assert_called_once_with(
                appointment=mock_appointment, key=FIELD_RECURRENCE_INTERVAL_KEY
            )

    def test_recurrence_interval_property_with_invalid_metadata(
        self, handler, mock_appointment
    ):
        """Test recurrence_interval property defaults to 1 when metadata is invalid."""
        handler._appointment = mock_appointment

        with patch(
            "recurring_appointments.handlers.recurrence.AppointmentMetadata.objects.filter"
        ) as mock_filter:
            mock_queryset = MagicMock()
            mock_queryset.values_list.return_value.first.return_value = "invalid"
            mock_filter.return_value = mock_queryset

            result = handler.recurrence_interval

            assert result == 1

    def test_recurrence_stops_after_property_with_valid_metadata(
        self, handler, mock_appointment
    ):
        """Test recurrence_stops_after property with valid metadata."""
        handler._appointment = mock_appointment

        with patch(
            "recurring_appointments.handlers.recurrence.AppointmentMetadata.objects.filter"
        ) as mock_filter:
            mock_queryset = MagicMock()
            mock_queryset.values_list.return_value.first.return_value = "10"
            mock_filter.return_value = mock_queryset

            result = handler.recurrence_stops_after

            assert result == 10
            mock_filter.assert_called_once_with(
                appointment=mock_appointment, key=FIELD_RECURRENCE_STOP_AFTER_KEY
            )

    def test_recurrence_stops_after_property_with_invalid_metadata(
        self, handler, mock_appointment
    ):
        """Test recurrence_stops_after property defaults to 30 when metadata is invalid."""
        handler._appointment = mock_appointment

        with patch(
            "recurring_appointments.handlers.recurrence.AppointmentMetadata.objects.filter"
        ) as mock_filter:
            mock_queryset = MagicMock()
            mock_queryset.values_list.return_value.first.return_value = None
            mock_filter.return_value = mock_queryset

            result = handler.recurrence_stops_after

            assert result == 30

    def test_calculate_recurrence_date_days(self, handler, mock_appointment):
        """Test _calculate_recurrence_date for daily recurrence."""
        handler._appointment = mock_appointment
        handler._recurrence_type = RecurrenceEnum.DAYS.value
        handler._recurrence_interval = 2

        result = handler._calculate_recurrence_date(3)

        # Should be 6 days later (3 * 2)
        expected = datetime.datetime(2025, 1, 21, 10, 0, 0)
        assert result == expected

    def test_calculate_recurrence_date_weeks(self, handler, mock_appointment):
        """Test _calculate_recurrence_date for weekly recurrence."""
        handler._appointment = mock_appointment
        handler._recurrence_type = RecurrenceEnum.WEEKS.value
        handler._recurrence_interval = 1

        result = handler._calculate_recurrence_date(2)

        # Should be 2 weeks later
        expected = datetime.datetime(2025, 1, 29, 10, 0, 0)
        assert result == expected

    def test_calculate_recurrence_date_months(self, handler, mock_appointment):
        """Test _calculate_recurrence_date for monthly recurrence."""
        handler._appointment = mock_appointment
        handler._recurrence_type = RecurrenceEnum.MONTHS.value
        handler._recurrence_interval = 1

        result = handler._calculate_recurrence_date(3)

        # Should be 3 months later
        expected = datetime.datetime(2025, 4, 15, 10, 0, 0)
        assert result == expected

    def test_calculate_recurrence_date_none(self, handler, mock_appointment):
        """Test _calculate_recurrence_date with no recurrence type."""
        handler._appointment = mock_appointment
        handler._recurrence_type = RecurrenceEnum.NONE.value
        handler._recurrence_interval = 1

        result = handler._calculate_recurrence_date(5)

        # Should return the original start time
        assert result == mock_appointment.start_time

    def test_create_child_appointment(self, handler, mock_appointment):
        """Test _create_child_appointment creates appointment with correct attributes."""
        handler._appointment = mock_appointment
        handler._recurrence_type = RecurrenceEnum.DAYS.value
        handler._recurrence_interval = 1

        with patch(
            "recurring_appointments.handlers.recurrence.Appointment"
        ) as mock_appointment_class:
            handler._create_child_appointment(2)

            # Verify Appointment was called with correct parameters
            mock_appointment_class.assert_called_once()
            call_kwargs = mock_appointment_class.call_args[1]

            assert call_kwargs["patient_id"] == "patient-123"
            assert call_kwargs["parent_appointment_id"] == "appointment-123"
            assert call_kwargs["duration_minutes"] == 30
            assert call_kwargs["provider_id"] == "provider-123"
            assert call_kwargs["practice_location_id"] == "location-123"
            assert call_kwargs["meeting_link"] == "https://example.com/meeting"
            assert call_kwargs["appointment_note_type_id"] == "note-type-123"
            # start_time should be 2 days later
            expected_time = datetime.datetime(2025, 1, 17, 10, 0, 0)
            assert call_kwargs["start_time"] == expected_time

    def test_create_child_event(self, handler, mock_appointment):
        """Test _create_child_event creates schedule event with correct attributes."""
        handler._appointment = mock_appointment
        handler._recurrence_type = RecurrenceEnum.WEEKS.value
        handler._recurrence_interval = 1

        with patch(
            "recurring_appointments.handlers.recurrence.ScheduleEvent"
        ) as mock_event_class:
            handler._create_child_event(1)

            # Verify ScheduleEvent was called with correct parameters
            mock_event_class.assert_called_once()
            call_kwargs = mock_event_class.call_args[1]

            assert call_kwargs["patient_id"] == "patient-123"
            assert call_kwargs["parent_appointment_id"] == "appointment-123"
            assert call_kwargs["description"] == "Test appointment"
            assert call_kwargs["duration_minutes"] == 30
            assert call_kwargs["practice_location_id"] == "location-123"
            assert call_kwargs["provider_id"] == "provider-123"
            assert call_kwargs["note_type_id"] == "note-type-123"
            # start_time should be 1 week later
            expected_time = datetime.datetime(2025, 1, 22, 10, 0, 0)
            assert call_kwargs["start_time"] == expected_time

    def test_compute_no_recurrence_type(self, handler, mock_appointment):
        """Test compute returns empty list when no recurrence type."""
        handler._appointment = mock_appointment

        with patch(
            "recurring_appointments.handlers.recurrence.AppointmentMetadata.objects.filter"
        ) as mock_filter:
            mock_queryset = MagicMock()
            mock_queryset.values_list.return_value.first.return_value = None
            mock_filter.return_value = mock_queryset

            result = handler.compute()

            assert result == []

    def test_compute_recurrence_type_none(self, handler, mock_appointment):
        """Test compute returns empty list when recurrence type is NONE."""
        handler._appointment = mock_appointment
        handler._recurrence_type = RecurrenceEnum.NONE.value

        result = handler.compute()

        assert result == []

    def test_compute_creates_appointments(self, handler, mock_appointment):
        """Test compute creates multiple child appointments."""
        handler._appointment = mock_appointment
        handler._recurrence_type = RecurrenceEnum.DAYS.value
        handler._recurrence_interval = 1
        handler._recurrence_stops_after = 3

        # Mock note type category as appointment (not schedule event)
        from canvas_sdk.v1.data.note import NoteTypeCategories

        mock_appointment.note_type.category = NoteTypeCategories.APPOINTMENT

        with patch(
            "recurring_appointments.handlers.recurrence.Appointment"
        ) as mock_appointment_class:
            mock_appt_instance = MagicMock()
            mock_created = MagicMock()
            mock_appt_instance.create.return_value = mock_created
            mock_appointment_class.return_value = mock_appt_instance

            result = handler.compute()

            # Should create 3 appointments
            assert len(result) == 3
            assert mock_appointment_class.call_count == 3
            assert mock_appt_instance.create.call_count == 3

    def test_compute_creates_schedule_events(self, handler, mock_appointment):
        """Test compute creates multiple child schedule events."""
        handler._appointment = mock_appointment
        handler._recurrence_type = RecurrenceEnum.WEEKS.value
        handler._recurrence_interval = 2
        handler._recurrence_stops_after = 2

        # Mock note type category as schedule event
        from canvas_sdk.v1.data.note import NoteTypeCategories

        mock_appointment.note_type.category = NoteTypeCategories.SCHEDULE_EVENT

        with patch(
            "recurring_appointments.handlers.recurrence.ScheduleEvent"
        ) as mock_event_class:
            mock_event_instance = MagicMock()
            mock_created = MagicMock()
            mock_event_instance.create.return_value = mock_created
            mock_event_class.return_value = mock_event_instance

            result = handler.compute()

            # Should create 2 schedule events
            assert len(result) == 2
            assert mock_event_class.call_count == 2
            assert mock_event_instance.create.call_count == 2
