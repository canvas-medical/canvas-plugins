"""Tests for recurring_appointments.handlers.form module."""

from unittest.mock import MagicMock, patch

from recurring_appointments.handlers.form import AppointmentFormFields
from recurring_appointments.utils.constants import (
    FIELD_RECURRENCE_INTERVAL_KEY,
    FIELD_RECURRENCE_TYPE_KEY,
    FIELD_RECURRENCE_STOP_AFTER_KEY,
)


class TestAppointmentFormFields:
    """Tests for AppointmentFormFields handler."""

    def test_responds_to_configuration(self):
        """Test that handler responds to the correct event type."""
        from canvas_sdk.events import EventType

        assert AppointmentFormFields.RESPONDS_TO == EventType.Name(
            EventType.APPOINTMENT__FORM__GET_ADDITIONAL_FIELDS
        )

    def test_inherits_from_base_handler(self):
        """Test that AppointmentFormFields inherits from BaseHandler."""
        from canvas_sdk.handlers import BaseHandler

        assert issubclass(AppointmentFormFields, BaseHandler)

    def test_compute_returns_form_effect(self):
        """Test that compute returns a form effect with correct fields."""
        mock_event = MagicMock()
        handler = AppointmentFormFields(event=mock_event)

        with patch(
            "recurring_appointments.handlers.form.AppointmentsMetadataCreateFormEffect"
        ) as mock_effect:
            mock_effect_instance = MagicMock()
            mock_applied = MagicMock()
            mock_effect_instance.apply.return_value = mock_applied
            mock_effect.return_value = mock_effect_instance

            result = handler.compute()

            # Verify effect was created with form fields
            mock_effect.assert_called_once()
            call_kwargs = mock_effect.call_args[1]
            form_fields = call_kwargs["form_fields"]

            # Should have 3 form fields
            assert len(form_fields) == 3

            # Check field keys
            field_keys = [field.key for field in form_fields]
            assert FIELD_RECURRENCE_INTERVAL_KEY in field_keys
            assert FIELD_RECURRENCE_TYPE_KEY in field_keys
            assert FIELD_RECURRENCE_STOP_AFTER_KEY in field_keys

            # Verify apply was called
            mock_effect_instance.apply.assert_called_once()

            # Verify result
            assert len(result) == 1
            assert result[0] == mock_applied

    def test_interval_field_has_correct_options(self):
        """Test that interval field has options from 1 to 8."""
        mock_event = MagicMock()
        handler = AppointmentFormFields(event=mock_event)

        with patch(
            "recurring_appointments.handlers.form.AppointmentsMetadataCreateFormEffect"
        ) as mock_effect:
            mock_effect_instance = MagicMock()
            mock_effect.return_value = mock_effect_instance

            handler.compute()

            call_kwargs = mock_effect.call_args[1]
            form_fields = call_kwargs["form_fields"]

            # Find interval field
            interval_field = next(
                field for field in form_fields if field.key == FIELD_RECURRENCE_INTERVAL_KEY
            )

            # Check options
            assert interval_field.options == ["1", "2", "3", "4", "5", "6", "7", "8"]
