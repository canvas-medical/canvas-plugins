"""Tests for appointment_state_field.handlers.form module."""

import json
from unittest.mock import MagicMock, patch

import pytest

from appointment_state_field.handlers.form import (
    AppointmentFormFields,
    AppointmentProviderFormField,
)
from appointment_state_field.utils.constants import FIELD_STATE_KEY, STATES


@pytest.fixture
def form_fields_handler():
    """Create an AppointmentFormFields handler instance with mocked event."""
    mock_event = MagicMock()
    return AppointmentFormFields(event=mock_event)


@pytest.fixture
def provider_form_field_handler():
    """Create an AppointmentProviderFormField handler instance with mocked event."""
    mock_event = MagicMock()
    return AppointmentProviderFormField(event=mock_event)


class TestAppointmentFormFields:
    """Tests for the AppointmentFormFields handler."""

    def test_responds_to_configuration(self):
        """Test that handler responds to the correct event type."""
        from canvas_sdk.events import EventType

        assert AppointmentFormFields.RESPONDS_TO == EventType.Name(
            EventType.APPOINTMENT__FORM__GET_ADDITIONAL_FIELDS
        )

    def test_compute_returns_list(self, form_fields_handler):
        """Test that compute() returns a list."""
        with patch(
            "appointment_state_field.handlers.form.AppointmentsMetadataCreateFormEffect"
        ) as mock_effect:
            mock_effect_instance = MagicMock()
            mock_effect_instance.apply.return_value = MagicMock()
            mock_effect.return_value = mock_effect_instance

            result = form_fields_handler.compute()

            assert isinstance(result, list)
            assert len(result) == 1

    def test_compute_creates_form_effect(self, form_fields_handler):
        """Test that compute() creates an AppointmentsMetadataCreateFormEffect."""
        with patch(
            "appointment_state_field.handlers.form.AppointmentsMetadataCreateFormEffect"
        ) as mock_effect:
            mock_effect_instance = MagicMock()
            mock_effect_instance.apply.return_value = MagicMock()
            mock_effect.return_value = mock_effect_instance

            form_fields_handler.compute()

            # Verify the effect was called
            mock_effect.assert_called_once()

            # Get the call arguments
            call_args = mock_effect.call_args
            form_fields = call_args[1]["form_fields"]

            # Verify form fields structure
            assert len(form_fields) == 1
            assert form_fields[0].key == FIELD_STATE_KEY
            assert form_fields[0].label == "State"
            assert form_fields[0].required is False
            assert form_fields[0].options == STATES

    def test_compute_applies_effect(self, form_fields_handler):
        """Test that compute() calls apply() on the effect."""
        with patch(
            "appointment_state_field.handlers.form.AppointmentsMetadataCreateFormEffect"
        ) as mock_effect:
            mock_effect_instance = MagicMock()
            mock_applied = MagicMock()
            mock_effect_instance.apply.return_value = mock_applied
            mock_effect.return_value = mock_effect_instance

            result = form_fields_handler.compute()

            mock_effect_instance.apply.assert_called_once()
            assert result[0] == mock_applied


class TestAppointmentProviderFormField:
    """Tests for the AppointmentProviderFormField handler."""

    def test_responds_to_configuration(self):
        """Test that handler responds to the correct event type."""
        from canvas_sdk.events import EventType

        assert AppointmentProviderFormField.RESPONDS_TO == EventType.Name(
            EventType.APPOINTMENT__FORM__PROVIDERS__POST_SEARCH
        )

    def test_compute_no_state_selected_returns_empty_list(
        self, provider_form_field_handler, monkeypatch
    ):
        """Test that compute() returns empty list when no state is selected."""
        dummy_context = {
            "providers": [{"value": "provider-1", "label": "Dr. Smith"}],
            "selected_values": {"additional_fields": []},
        }
        monkeypatch.setattr(
            type(provider_form_field_handler), "context", property(lambda self: dummy_context)
        )

        result = provider_form_field_handler.compute()

        assert result == []

    def test_compute_empty_state_value_returns_empty_list(
        self, provider_form_field_handler, monkeypatch
    ):
        """Test that compute() returns empty list when state value is empty string."""
        dummy_context = {
            "providers": [{"value": "provider-1", "label": "Dr. Smith"}],
            "selected_values": {
                "additional_fields": [{"key": FIELD_STATE_KEY, "values": ""}]
            },
        }
        monkeypatch.setattr(
            type(provider_form_field_handler), "context", property(lambda self: dummy_context)
        )

        result = provider_form_field_handler.compute()

        assert result == []

    def test_compute_filters_providers_by_license(
        self, provider_form_field_handler, monkeypatch
    ):
        """Test that compute() filters providers based on their licenses."""
        dummy_context = {
            "providers": [
                {"value": "provider-1", "label": "Dr. Smith"},
                {"value": "provider-2", "label": "Dr. Jones"},
            ],
            "selected_values": {
                "additional_fields": [{"key": FIELD_STATE_KEY, "values": "California"}]
            },
        }
        monkeypatch.setattr(
            type(provider_form_field_handler), "context", property(lambda self: dummy_context)
        )

        # Mock Staff.objects.filter
        with patch("appointment_state_field.handlers.form.Staff.objects.filter") as mock_filter:
            # Mock staff with California license
            mock_staff_1 = MagicMock()
            mock_licenses_1 = MagicMock()
            mock_licenses_1.filter.return_value.exists.return_value = True
            mock_staff_1.licenses = mock_licenses_1

            # Mock staff without California license
            mock_staff_2 = MagicMock()
            mock_licenses_2 = MagicMock()
            mock_licenses_2.filter.return_value.exists.return_value = False
            mock_staff_2.licenses = mock_licenses_2

            # Configure the filter to return different staff for different IDs
            def filter_side_effect(id):
                mock_queryset = MagicMock()
                if id == "provider-1":
                    mock_queryset.first.return_value = mock_staff_1
                elif id == "provider-2":
                    mock_queryset.first.return_value = mock_staff_2
                else:
                    mock_queryset.first.return_value = None
                return mock_queryset

            mock_filter.side_effect = filter_side_effect

            result = provider_form_field_handler.compute()

            # Verify result structure
            assert len(result) == 1
            effect = result[0]

            from canvas_sdk.effects import EffectType
            assert effect.type == EffectType.APPOINTMENT__FORM__PROVIDERS__POST_SEARCH_RESULTS

            # Parse the payload
            payload = json.loads(effect.payload)
            providers = payload["providers"]

            # Only provider-1 should be in the results
            assert len(providers) == 1
            assert providers[0]["value"] == "provider-1"
            assert providers[0]["label"] == "Dr. Smith"

    def test_compute_with_no_matching_providers(
        self, provider_form_field_handler, monkeypatch
    ):
        """Test that compute() returns empty provider list when no providers match."""
        dummy_context = {
            "providers": [
                {"value": "provider-1", "label": "Dr. Smith"},
            ],
            "selected_values": {
                "additional_fields": [{"key": FIELD_STATE_KEY, "values": "California"}]
            },
        }
        monkeypatch.setattr(
            type(provider_form_field_handler), "context", property(lambda self: dummy_context)
        )

        # Mock Staff.objects.filter
        with patch("appointment_state_field.handlers.form.Staff.objects.filter") as mock_filter:
            # Mock staff without California license
            mock_staff = MagicMock()
            mock_licenses = MagicMock()
            mock_licenses.filter.return_value.exists.return_value = False
            mock_staff.licenses = mock_licenses

            mock_queryset = MagicMock()
            mock_queryset.first.return_value = mock_staff
            mock_filter.return_value = mock_queryset

            result = provider_form_field_handler.compute()

            # Verify result structure
            assert len(result) == 1
            effect = result[0]

            # Parse the payload
            payload = json.loads(effect.payload)
            providers = payload["providers"]

            # No providers should be in the results
            assert len(providers) == 0

    def test_compute_with_nonexistent_staff(
        self, provider_form_field_handler, monkeypatch
    ):
        """Test that compute() handles nonexistent staff gracefully."""
        dummy_context = {
            "providers": [
                {"value": "nonexistent-provider", "label": "Dr. Ghost"},
            ],
            "selected_values": {
                "additional_fields": [{"key": FIELD_STATE_KEY, "values": "California"}]
            },
        }
        monkeypatch.setattr(
            type(provider_form_field_handler), "context", property(lambda self: dummy_context)
        )

        # Mock Staff.objects.filter to return None
        with patch("appointment_state_field.handlers.form.Staff.objects.filter") as mock_filter:
            mock_queryset = MagicMock()
            mock_queryset.first.return_value = None
            mock_filter.return_value = mock_queryset

            result = provider_form_field_handler.compute()

            # Verify result structure
            assert len(result) == 1
            effect = result[0]

            # Parse the payload
            payload = json.loads(effect.payload)
            providers = payload["providers"]

            # No providers should be in the results
            assert len(providers) == 0

    def test_compute_verifies_license_state(self, provider_form_field_handler, monkeypatch):
        """Test that compute() checks for the correct state abbreviation in licenses."""
        dummy_context = {
            "providers": [
                {"value": "provider-1", "label": "Dr. Smith"},
            ],
            "selected_values": {
                "additional_fields": [{"key": FIELD_STATE_KEY, "values": "New York"}]
            },
        }
        monkeypatch.setattr(
            type(provider_form_field_handler), "context", property(lambda self: dummy_context)
        )

        # Mock Staff.objects.filter
        with patch("appointment_state_field.handlers.form.Staff.objects.filter") as mock_filter:
            mock_staff = MagicMock()
            mock_licenses = MagicMock()
            mock_licenses_filtered = MagicMock()
            mock_licenses_filtered.exists.return_value = True
            mock_licenses.filter.return_value = mock_licenses_filtered
            mock_staff.licenses = mock_licenses

            mock_queryset = MagicMock()
            mock_queryset.first.return_value = mock_staff
            mock_filter.return_value = mock_queryset

            provider_form_field_handler.compute()

            # Verify that licenses were filtered with the correct state abbreviation (NY)
            mock_licenses.filter.assert_called_once_with(state="NY")
