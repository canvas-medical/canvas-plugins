"""Tests for patient_app_schedule.protocols.filters module."""

import json
from unittest.mock import MagicMock, patch

import pytest

from patient_app_schedule.protocols.filters import Providers, Locations


class TestProviders:
    """Tests for Providers handler."""

    def test_responds_to_configuration(self):
        """Test that handler responds to the correct event type."""
        from canvas_sdk.events import EventType

        assert Providers.RESPONDS_TO == EventType.Name(
            EventType.PATIENT_PORTAL__APPOINTMENTS__FORM_PROVIDERS__POST_SEARCH
        )

    def test_inherits_from_base_handler(self):
        """Test that Providers inherits from BaseHandler."""
        from canvas_sdk.handlers import BaseHandler

        assert issubclass(Providers, BaseHandler)

    def test_compute_no_providers_returns_empty(self):
        """Test that compute returns empty list when no providers in context."""
        mock_event = MagicMock()
        mock_event.context = {"providers": []}
        handler = Providers(event=mock_event)

        result = handler.compute()

        assert result == []

    def test_compute_no_patient_id_returns_all_providers(self):
        """Test that compute returns all providers when no patient ID found."""
        mock_event = MagicMock()
        providers = [
            {"id": "provider-1", "name": "Dr. Smith"},
            {"id": "provider-2", "name": "Dr. Jones"},
        ]
        mock_event.context = {"providers": providers}
        mock_event.target.id = None
        handler = Providers(event=mock_event)

        result = handler.compute()

        assert len(result) == 1
        payload = json.loads(result[0].payload)
        assert payload["providers"] == providers

    def test_compute_filters_providers_by_care_team(self):
        """Test that compute filters providers to only care team members."""
        mock_event = MagicMock()
        providers = [
            {"id": "provider-1", "name": "Dr. Smith"},
            {"id": "provider-2", "name": "Dr. Jones"},
            {"id": "provider-3", "name": "Dr. Wilson"},
        ]
        mock_event.context = {"providers": providers}
        mock_event.target.id = "patient-123"
        handler = Providers(event=mock_event)

        with patch.object(
            handler, "_get_care_team_provider_ids", return_value={"provider-1", "provider-3"}
        ):
            result = handler.compute()

        assert len(result) == 1
        payload = json.loads(result[0].payload)
        assert len(payload["providers"]) == 2
        assert payload["providers"][0]["id"] == "provider-1"
        assert payload["providers"][1]["id"] == "provider-3"

    def test_compute_handles_exception_gracefully(self):
        """Test that compute returns all providers when an exception occurs."""
        mock_event = MagicMock()
        providers = [{"id": "provider-1", "name": "Dr. Smith"}]
        mock_event.context = {"providers": providers}
        mock_event.target.id = "patient-123"
        handler = Providers(event=mock_event)

        with patch.object(handler, "_get_care_team_provider_ids", side_effect=Exception("DB error")):
            result = handler.compute()

        # Should return all providers on error
        assert len(result) == 1
        payload = json.loads(result[0].payload)
        assert payload["providers"] == providers

    def test_compute_filters_to_empty_when_no_care_team_match(self):
        """Test that compute returns empty list when no providers match care team."""
        mock_event = MagicMock()
        providers = [
            {"id": "provider-1", "name": "Dr. Smith"},
            {"id": "provider-2", "name": "Dr. Jones"},
        ]
        mock_event.context = {"providers": providers}
        mock_event.target.id = "patient-123"
        handler = Providers(event=mock_event)

        with patch.object(handler, "_get_care_team_provider_ids", return_value={"provider-99"}):
            result = handler.compute()

        assert len(result) == 1
        payload = json.loads(result[0].payload)
        assert payload["providers"] == []

    def test_get_care_team_provider_ids(self):
        """Test _get_care_team_provider_ids retrieves correct IDs."""
        mock_event = MagicMock()
        handler = Providers(event=mock_event)

        with patch(
            "patient_app_schedule.protocols.filters.CareTeamMembership.objects.filter"
        ) as mock_filter:
            mock_queryset = MagicMock()
            mock_queryset.values_list.return_value = ["provider-1", "provider-2"]
            mock_filter.return_value = mock_queryset

            result = handler._get_care_team_provider_ids("patient-123")

            assert result == {"provider-1", "provider-2"}
            mock_filter.assert_called_once()

    def test_get_care_team_provider_ids_handles_exception(self):
        """Test _get_care_team_provider_ids returns empty set on exception."""
        mock_event = MagicMock()
        handler = Providers(event=mock_event)

        with patch(
            "patient_app_schedule.protocols.filters.CareTeamMembership.objects.filter",
            side_effect=Exception("DB error"),
        ):
            result = handler._get_care_team_provider_ids("patient-123")

        assert result == set()

    def test_create_effect_formats_payload_correctly(self):
        """Test _create_effect creates effect with correct structure."""
        mock_event = MagicMock()
        handler = Providers(event=mock_event)

        providers = [{"id": "provider-1", "name": "Dr. Smith"}]
        result = handler._create_effect(providers)

        assert len(result) == 1
        effect = result[0]
        payload = json.loads(effect.payload)
        assert payload["providers"] == providers

    def test_create_effect_uses_correct_effect_type(self):
        """Test _create_effect uses the correct effect type."""
        from canvas_sdk.effects import EffectType

        mock_event = MagicMock()
        handler = Providers(event=mock_event)

        result = handler._create_effect([])

        assert len(result) == 1
        assert (
            result[0].type
            == EffectType.PATIENT_PORTAL__APPOINTMENTS__FORM_PROVIDERS__POST_SEARCH_RESULTS
        )


class TestLocations:
    """Tests for Locations handler."""

    def test_responds_to_configuration(self):
        """Test that handler responds to the correct event type."""
        from canvas_sdk.events import EventType

        assert Locations.RESPONDS_TO == EventType.Name(
            EventType.PATIENT_PORTAL__APPOINTMENTS__FORM_LOCATIONS__POST_SEARCH
        )

    def test_inherits_from_base_handler(self):
        """Test that Locations inherits from BaseHandler."""
        from canvas_sdk.handlers import BaseHandler

        assert issubclass(Locations, BaseHandler)

    def test_compute_no_locations_returns_empty(self):
        """Test that compute returns empty list when no locations in context."""
        mock_event = MagicMock()
        mock_event.context = {"locations": []}
        handler = Locations(event=mock_event)

        result = handler.compute()

        assert result == []

    def test_compute_no_patient_id_returns_all_locations(self):
        """Test that compute returns all locations when no patient ID found."""
        mock_event = MagicMock()
        locations = [
            {"id": "location-1", "name": "Main Office"},
            {"id": "location-2", "name": "Downtown Clinic"},
        ]
        mock_event.context = {"locations": locations}
        mock_event.target.id = None
        handler = Locations(event=mock_event)

        result = handler.compute()

        assert len(result) == 1
        payload = json.loads(result[0].payload)
        assert payload["locations"] == locations

    def test_compute_filters_locations_by_appointment_history(self):
        """Test that compute filters locations to only those with appointments."""
        mock_event = MagicMock()
        locations = [
            {"id": "location-1", "name": "Main Office"},
            {"id": "location-2", "name": "Downtown Clinic"},
            {"id": "location-3", "name": "Uptown Center"},
        ]
        mock_event.context = {"locations": locations}
        mock_event.target.id = "patient-123"
        handler = Locations(event=mock_event)

        with patch.object(
            handler, "_get_patient_location_ids", return_value={"location-1", "location-3"}
        ):
            result = handler.compute()

        assert len(result) == 1
        payload = json.loads(result[0].payload)
        assert len(payload["locations"]) == 2
        assert payload["locations"][0]["id"] == "location-1"
        assert payload["locations"][1]["id"] == "location-3"

    def test_compute_handles_exception_gracefully(self):
        """Test that compute returns all locations when an exception occurs."""
        mock_event = MagicMock()
        locations = [{"id": "location-1", "name": "Main Office"}]
        mock_event.context = {"locations": locations}
        mock_event.target.id = "patient-123"
        handler = Locations(event=mock_event)

        with patch.object(
            handler, "_get_patient_location_ids", side_effect=Exception("DB error")
        ):
            result = handler.compute()

        # Should return all locations on error
        assert len(result) == 1
        payload = json.loads(result[0].payload)
        assert payload["locations"] == locations

    def test_compute_filters_to_empty_when_no_location_match(self):
        """Test that compute returns empty list when no locations match history."""
        mock_event = MagicMock()
        locations = [
            {"id": "location-1", "name": "Main Office"},
            {"id": "location-2", "name": "Downtown Clinic"},
        ]
        mock_event.context = {"locations": locations}
        mock_event.target.id = "patient-123"
        handler = Locations(event=mock_event)

        with patch.object(handler, "_get_patient_location_ids", return_value={"location-99"}):
            result = handler.compute()

        assert len(result) == 1
        payload = json.loads(result[0].payload)
        assert payload["locations"] == []

    def test_get_patient_location_ids(self):
        """Test _get_patient_location_ids retrieves correct IDs."""
        mock_event = MagicMock()
        handler = Locations(event=mock_event)

        with patch(
            "patient_app_schedule.protocols.filters.Appointment.objects.filter"
        ) as mock_filter:
            mock_queryset = MagicMock()
            mock_queryset.exclude.return_value.values_list.return_value.distinct.return_value = [
                "location-1",
                "location-2",
            ]
            mock_filter.return_value = mock_queryset

            result = handler._get_patient_location_ids("patient-123")

            assert result == {"location-1", "location-2"}
            mock_filter.assert_called_once()

    def test_get_patient_location_ids_handles_exception(self):
        """Test _get_patient_location_ids returns empty set on exception."""
        mock_event = MagicMock()
        handler = Locations(event=mock_event)

        with patch(
            "patient_app_schedule.protocols.filters.Appointment.objects.filter",
            side_effect=Exception("DB error"),
        ):
            result = handler._get_patient_location_ids("patient-123")

        assert result == set()

    def test_create_effect_formats_payload_correctly(self):
        """Test _create_effect creates effect with correct structure."""
        mock_event = MagicMock()
        handler = Locations(event=mock_event)

        locations = [{"id": "location-1", "name": "Main Office"}]
        result = handler._create_effect(locations)

        assert len(result) == 1
        effect = result[0]
        payload = json.loads(effect.payload)
        assert payload["locations"] == locations

    def test_create_effect_uses_correct_effect_type(self):
        """Test _create_effect uses the correct effect type."""
        from canvas_sdk.effects import EffectType

        mock_event = MagicMock()
        handler = Locations(event=mock_event)

        result = handler._create_effect([])

        assert len(result) == 1
        assert (
            result[0].type
            == EffectType.PATIENT_PORTAL__APPOINTMENTS__FORM_LOCATIONS__POST_SEARCH_RESULTS
        )
