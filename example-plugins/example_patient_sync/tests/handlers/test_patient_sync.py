"""Tests for example_patient_sync.handlers.patient_sync module."""

import datetime
from unittest.mock import MagicMock, patch

import pytest

from example_patient_sync.handlers.patient_sync import PatientSync


@pytest.fixture
def mock_event():
    """Create a mock event with target."""
    event = MagicMock()
    event.target.id = "patient-123"
    return event


@pytest.fixture
def handler(mock_event):
    """Create a PatientSync handler with mocked secrets."""
    handler = PatientSync(event=mock_event)
    handler.secrets = {
        "PARTNER_URL_BASE": "https://partner.example.com",
        "PARTNER_API_BASE_URL": "https://api.partner.example.com",
        "PARTNER_SECRET_API_KEY": "secret-key-123",
    }
    handler.environment = {"CUSTOMER_IDENTIFIER": "test-customer"}
    return handler


@pytest.fixture
def mock_patient():
    """Create a mock Canvas patient."""
    patient = MagicMock()
    patient.id = "patient-123"
    patient.first_name = "John"
    patient.last_name = "Doe"
    patient.birth_date = datetime.date(1990, 1, 15)
    return patient


class TestPatientSync:
    """Tests for PatientSync handler."""

    def test_responds_to_configuration(self):
        """Test that handler responds to the correct event types."""
        from canvas_sdk.events import EventType

        assert PatientSync.RESPONDS_TO == [
            EventType.Name(EventType.PATIENT_CREATED),
        ]

    def test_inherits_from_base_handler(self):
        """Test that PatientSync inherits from BaseHandler."""
        from canvas_sdk.handlers.base import BaseHandler

        assert issubclass(PatientSync, BaseHandler)

    def test_partner_url_base_property(self, handler):
        """Test that partner_url_base returns value from secrets."""
        assert handler.partner_url_base == "https://partner.example.com"

    def test_partner_api_base_url_method(self, handler):
        """Test that partner_api_base_url returns value from secrets."""
        assert handler.partner_api_base_url() == "https://api.partner.example.com"

    def test_partner_request_headers_property(self, handler):
        """Test that partner_request_headers returns correct headers."""
        headers = handler.partner_request_headers
        assert headers == {"X-API-Key": "secret-key-123"}

    def test_partner_patient_metadata_property(self, handler):
        """Test that partner_patient_metadata returns correct metadata."""
        metadata = handler.partner_patient_metadata
        assert metadata["canvasPatientId"] == "patient-123"
        assert metadata["canvasUrl"] == "https://test-customer.canvasmedical.com"

    def test_lookup_external_id_by_system_url_found(self, handler):
        """Test lookup_external_id_by_system_url when ID exists."""
        mock_patient = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.values_list.return_value.first.return_value = "external-123"
        mock_patient.external_identifiers.filter.return_value = mock_queryset

        result = handler.lookup_external_id_by_system_url(
            mock_patient, "https://system.example.com"
        )

        assert result == "external-123"
        mock_patient.external_identifiers.filter.assert_called_once_with(
            system="https://system.example.com"
        )

    def test_lookup_external_id_by_system_url_not_found(self, handler):
        """Test lookup_external_id_by_system_url when ID doesn't exist."""
        mock_patient = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.values_list.return_value.first.return_value = None
        mock_patient.external_identifiers.filter.return_value = mock_queryset

        result = handler.lookup_external_id_by_system_url(
            mock_patient, "https://system.example.com"
        )

        assert result is None

    def test_get_patient_from_system_api(self, handler):
        """Test get_patient_from_system_api makes correct HTTP request."""
        with patch("example_patient_sync.handlers.patient_sync.Http") as mock_http_class:
            mock_http = MagicMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"id": "external-456"}
            mock_http.get.return_value = mock_response
            mock_http_class.return_value = mock_http

            result = handler.get_patient_from_system_api("patient-123")

            assert result == mock_response
            # Verify HTTP get was called once with correct headers
            mock_http.get.assert_called_once()
            call_args = mock_http.get.call_args
            # Check that patient ID is in the URL
            assert "patient-123" in call_args[0][0]
            assert call_args[1]["headers"] == {"X-API-Key": "secret-key-123"}

    def test_compute_patient_already_has_external_id_no_update_needed(
        self, handler, mock_patient
    ):
        """Test compute when patient already has external ID and no update needed."""
        # Mock patient already has external ID
        mock_queryset = MagicMock()
        mock_queryset.values_list.return_value.first.return_value = "external-456"
        mock_patient.external_identifiers.filter.return_value = mock_queryset

        with patch("example_patient_sync.handlers.patient_sync.Patient.objects.get") as mock_get:
            mock_get.return_value = mock_patient

            with patch("example_patient_sync.handlers.patient_sync.Http") as mock_http_class:
                mock_http = MagicMock()
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"id": "external-456"}
                mock_http.post.return_value = mock_response
                mock_http_class.return_value = mock_http

                result = handler.compute()

                # Should return empty list (no external ID update needed)
                assert result == []

                # Verify the POST request was made with correct URL (includes external ID)
                mock_http.post.assert_called_once()
                call_args = mock_http.post.call_args
                assert "external-456" in call_args[0][0]
                assert call_args[1]["json"]["externalId"] == "patient-123"
                assert call_args[1]["json"]["firstName"] == "John"
                assert call_args[1]["json"]["lastName"] == "Doe"
                assert call_args[1]["json"]["dateOfBirth"] == "1990-01-15"

    def test_compute_patient_exists_in_external_system_update_canvas(
        self, handler, mock_patient
    ):
        """Test compute when patient exists in external system, need to update Canvas."""
        # Mock patient doesn't have external ID in Canvas
        mock_queryset = MagicMock()
        mock_queryset.values_list.return_value.first.return_value = None
        mock_patient.external_identifiers.filter.return_value = mock_queryset

        with patch("example_patient_sync.handlers.patient_sync.Patient.objects.get") as mock_get:
            mock_get.return_value = mock_patient

            with patch("example_patient_sync.handlers.patient_sync.Http") as mock_http_class:
                mock_http = MagicMock()

                # First GET returns patient exists in external system
                mock_get_response = MagicMock()
                mock_get_response.status_code = 200
                mock_get_response.json.return_value = {"id": "external-789"}
                mock_http.get.return_value = mock_get_response

                # POST to update patient
                mock_post_response = MagicMock()
                mock_post_response.status_code = 200
                mock_post_response.json.return_value = {"id": "external-789"}
                mock_http.post.return_value = mock_post_response

                mock_http_class.return_value = mock_http

                with patch(
                    "example_patient_sync.handlers.patient_sync.CreatePatientExternalIdentifier"
                ) as mock_create_effect:
                    mock_effect_instance = MagicMock()
                    mock_created_effect = MagicMock()
                    mock_effect_instance.create.return_value = mock_created_effect
                    mock_create_effect.return_value = mock_effect_instance

                    result = handler.compute()

                    # Should return effect to update Canvas with external ID
                    assert len(result) == 1
                    assert result[0] == mock_created_effect

                    # Verify CreatePatientExternalIdentifier was called correctly
                    mock_create_effect.assert_called_once_with(
                        patient_id="patient-123",
                        system="https://partner.example.com",
                        value="external-789",
                    )

    def test_compute_patient_not_in_external_system_create_new(self, handler, mock_patient):
        """Test compute when patient doesn't exist in external system, create new."""
        # Mock patient doesn't have external ID in Canvas
        mock_queryset = MagicMock()
        mock_queryset.values_list.return_value.first.return_value = None
        mock_patient.external_identifiers.filter.return_value = mock_queryset

        with patch("example_patient_sync.handlers.patient_sync.Patient.objects.get") as mock_get:
            mock_get.return_value = mock_patient

            with patch("example_patient_sync.handlers.patient_sync.Http") as mock_http_class:
                mock_http = MagicMock()

                # First GET returns patient doesn't exist (404 or similar)
                mock_get_response = MagicMock()
                mock_get_response.status_code = 404
                mock_http.get.return_value = mock_get_response

                # POST creates new patient and returns new ID
                mock_post_response = MagicMock()
                mock_post_response.status_code = 201
                mock_post_response.json.return_value = {"id": "external-new-123"}
                mock_http.post.return_value = mock_post_response

                mock_http_class.return_value = mock_http

                with patch(
                    "example_patient_sync.handlers.patient_sync.CreatePatientExternalIdentifier"
                ) as mock_create_effect:
                    mock_effect_instance = MagicMock()
                    mock_created_effect = MagicMock()
                    mock_effect_instance.create.return_value = mock_created_effect
                    mock_create_effect.return_value = mock_effect_instance

                    result = handler.compute()

                    # Should return effect to update Canvas with new external ID
                    assert len(result) == 1
                    assert result[0] == mock_created_effect

                    # Verify CreatePatientExternalIdentifier was called with new ID
                    mock_create_effect.assert_called_once_with(
                        patient_id="patient-123",
                        system="https://partner.example.com",
                        value="external-new-123",
                    )

    def test_compute_duplicate_patient_returns_empty(self, handler, mock_patient):
        """Test compute returns empty list when duplicate patient detected (409)."""
        # Mock patient doesn't have external ID in Canvas
        mock_queryset = MagicMock()
        mock_queryset.values_list.return_value.first.return_value = None
        mock_patient.external_identifiers.filter.return_value = mock_queryset

        with patch("example_patient_sync.handlers.patient_sync.Patient.objects.get") as mock_get:
            mock_get.return_value = mock_patient

            with patch("example_patient_sync.handlers.patient_sync.Http") as mock_http_class:
                mock_http = MagicMock()

                # First GET returns patient doesn't exist
                mock_get_response = MagicMock()
                mock_get_response.status_code = 404
                mock_http.get.return_value = mock_get_response

                # POST returns 409 (duplicate)
                mock_post_response = MagicMock()
                mock_post_response.status_code = 409
                mock_post_response.json.return_value = {"error": "Duplicate patient"}
                mock_http.post.return_value = mock_post_response

                mock_http_class.return_value = mock_http

                result = handler.compute()

                # Should return empty list (early return for duplicate)
                assert result == []

    def test_compute_builds_correct_payload(self, handler, mock_patient):
        """Test compute builds correct payload for partner API."""
        # Mock patient already has external ID
        mock_queryset = MagicMock()
        mock_queryset.values_list.return_value.first.return_value = "external-999"
        mock_patient.external_identifiers.filter.return_value = mock_queryset

        with patch("example_patient_sync.handlers.patient_sync.Patient.objects.get") as mock_get:
            mock_get.return_value = mock_patient

            with patch("example_patient_sync.handlers.patient_sync.Http") as mock_http_class:
                mock_http = MagicMock()
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"id": "external-999"}
                mock_http.post.return_value = mock_response
                mock_http_class.return_value = mock_http

                handler.compute()

                # Verify payload structure
                call_args = mock_http.post.call_args
                payload = call_args[1]["json"]
                assert payload["externalId"] == "patient-123"
                assert payload["firstName"] == "John"
                assert payload["lastName"] == "Doe"
                assert payload["dateOfBirth"] == "1990-01-15"
