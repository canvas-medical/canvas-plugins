"""Comprehensive tests for FullscriptAPI endpoints."""

import json
from datetime import datetime, timezone, timedelta
from http import HTTPStatus
from unittest.mock import Mock, patch

from fullscript.api.fullscriptAPI import FullscriptAPI


class DummyRequest:
    """A dummy request object for testing FullscriptAPI."""

    def __init__(self, json_body=None):
        self._json_body = json_body or {}

    def json(self):
        return self._json_body


class DummyEvent:
    """A dummy event object for testing API handlers."""

    def __init__(self, context=None):
        self.context = context or {"method": "POST", "path": "/app"}


class DummyCredentials:
    """Dummy credentials for staff session authentication tests."""

    def __init__(self, user_id):
        self.user_id = user_id


class TestFullscriptAPI:
    """Test suite for FullscriptAPI endpoints."""

    def test_api_prefix_configuration(self):
        """Test that the API has correct prefix configuration."""
        assert FullscriptAPI.PREFIX == "/app"

    # ==================== exchange_token tests ====================

    def test_exchange_token_with_valid_code(self):
        """Test token exchange with valid authorization code."""
        # Setup request
        request = DummyRequest(json_body={
            "code": "auth_code_123",
            "redirect_uri": "https://example.com/callback"
        })

        # Create API instance
        api = FullscriptAPI(event=DummyEvent())
        api.request = request
        api.secrets = {
            "FULLSCRIPT_CLIENT_ID": "client_id",
            "FULLSCRIPT_CLIENT_SECRET": "client_secret"
        }

        # Mock Staff query
        mock_staff_objects = Mock()
        mock_staff_objects.values_list.return_value.get.return_value = "staff-123"

        # Mock cache
        mock_cache = Mock()
        mock_cache.get.return_value = None  # No existing token

        # Mock requests.post for token exchange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "oauth": {
                "access_token": "new_access_token",
                "refresh_token": "new_refresh_token",
                "expires_in": 3600,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        }

        with patch("fullscript.api.fullscriptAPI.Staff") as mock_staff:
            mock_staff.objects = mock_staff_objects
            with patch("fullscript.api.fullscriptAPI.get_cache", return_value=mock_cache):
                with patch("fullscript.api.fullscriptAPI.requests.post", return_value=mock_response):
                    # Set request headers
                    api.request.headers = {"canvas-logged-in-user-id": "staff-123"}

                    result = api.exchange_token()

        # Verify response
        assert len(result) == 1
        response = result[0]
        assert response.status_code == HTTPStatus.OK

        data = json.loads(response.content.decode())
        assert data["token"] == "new_access_token"

        # Verify cache was updated
        mock_cache.set.assert_called_once()

    def test_exchange_token_with_valid_refresh_token(self):
        """Test token exchange using cached refresh token."""
        # Setup request
        request = DummyRequest(json_body={
            "code": None,
            "redirect_uri": "https://example.com/callback"
        })

        # Create API instance
        api = FullscriptAPI(event=DummyEvent())
        api.request = request
        api.secrets = {
            "FULLSCRIPT_CLIENT_ID": "client_id",
            "FULLSCRIPT_CLIENT_SECRET": "client_secret"
        }

        # Mock Staff query
        mock_staff_objects = Mock()
        mock_staff_objects.values_list.return_value.get.return_value = "staff-123"

        # Mock cache with existing expired token
        expires_in = 3600
        created_at = (datetime.now(timezone.utc) - timedelta(seconds=7200)).isoformat()  # Expired 2 hours ago

        mock_cache = Mock()
        mock_cache.get.return_value = {
            "access_token": "old_access_token",
            "refresh_token": "refresh_token_123",
            "expires_in": expires_in,
            "created_at": created_at
        }

        # Mock requests.post for token refresh
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "oauth": {
                "access_token": "refreshed_access_token",
                "refresh_token": "new_refresh_token",
                "expires_in": 3600,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        }

        with patch("fullscript.api.fullscriptAPI.Staff") as mock_staff:
            mock_staff.objects = mock_staff_objects
            with patch("fullscript.api.fullscriptAPI.get_cache", return_value=mock_cache):
                with patch("fullscript.api.fullscriptAPI.requests.post", return_value=mock_response):
                    api.request.headers = {"canvas-logged-in-user-id": "staff-123"}

                    result = api.exchange_token()

        # Verify response
        assert len(result) == 1
        response = result[0]
        assert response.status_code == HTTPStatus.OK

        data = json.loads(response.content.decode())
        assert data["token"] == "refreshed_access_token"

    def test_exchange_token_with_valid_cached_token(self):
        """Test token exchange with valid cached token (not expired)."""
        # Setup request
        request = DummyRequest(json_body={
            "code": None,
            "redirect_uri": "https://example.com/callback"
        })

        # Create API instance
        api = FullscriptAPI(event=DummyEvent())
        api.request = request
        api.secrets = {
            "FULLSCRIPT_CLIENT_ID": "client_id",
            "FULLSCRIPT_CLIENT_SECRET": "client_secret"
        }

        # Mock Staff query
        mock_staff_objects = Mock()
        mock_staff_objects.values_list.return_value.get.return_value = "staff-123"

        # Mock cache with valid token
        expires_in = 3600
        created_at = datetime.now(timezone.utc).isoformat()

        mock_cache = Mock()
        mock_cache.get.return_value = {
            "access_token": "valid_access_token",
            "refresh_token": "refresh_token_123",
            "expires_in": expires_in,
            "created_at": created_at
        }

        with patch("fullscript.api.fullscriptAPI.Staff") as mock_staff:
            mock_staff.objects = mock_staff_objects
            with patch("fullscript.api.fullscriptAPI.get_cache", return_value=mock_cache):
                api.request.headers = {"canvas-logged-in-user-id": "staff-123"}

                result = api.exchange_token()

        # Verify response returns cached token without API call
        assert len(result) == 1
        response = result[0]
        assert response.status_code == HTTPStatus.OK

        data = json.loads(response.content.decode())
        assert data["token"] == "valid_access_token"

    def test_exchange_token_failure(self):
        """Test token exchange handles API failure."""
        # Setup request
        request = DummyRequest(json_body={
            "code": "invalid_code",
            "redirect_uri": "https://example.com/callback"
        })

        # Create API instance
        api = FullscriptAPI(event=DummyEvent())
        api.request = request
        api.secrets = {
            "FULLSCRIPT_CLIENT_ID": "client_id",
            "FULLSCRIPT_CLIENT_SECRET": "client_secret"
        }

        # Mock Staff query
        mock_staff_objects = Mock()
        mock_staff_objects.values_list.return_value.get.return_value = "staff-123"

        # Mock cache
        mock_cache = Mock()
        mock_cache.get.return_value = None

        # Mock requests.post with failure
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Invalid authorization code"

        with patch("fullscript.api.fullscriptAPI.Staff") as mock_staff:
            mock_staff.objects = mock_staff_objects
            with patch("fullscript.api.fullscriptAPI.get_cache", return_value=mock_cache):
                with patch("fullscript.api.fullscriptAPI.requests.post", return_value=mock_response):
                    api.request.headers = {"canvas-logged-in-user-id": "staff-123"}

                    result = api.exchange_token()

        # Verify error response
        assert len(result) == 1
        response = result[0]
        assert response.status_code == HTTPStatus.BAD_GATEWAY

        data = json.loads(response.content.decode())
        assert "error" in data
        assert data["error"] == "Failed to exchange token"

    # ==================== create_session_grant tests ====================

    def test_create_session_grant_success(self):
        """Test session grant creation with valid access token."""
        # Setup request
        request = DummyRequest(json_body={
            "access_token": "valid_access_token"
        })

        # Create API instance
        api = FullscriptAPI(event=DummyEvent())
        api.request = request

        # Mock requests.post for session grant
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "secret_token": "session_grant_token_xyz"
        }

        with patch("fullscript.api.fullscriptAPI.requests.post", return_value=mock_response):
            result = api.create_session_grant()

        # Verify response
        assert len(result) == 1
        response = result[0]
        assert response.status_code == HTTPStatus.OK

        data = json.loads(response.content.decode())
        assert data["token"] == "session_grant_token_xyz"

    def test_create_session_grant_missing_token(self):
        """Test session grant creation without access token."""
        # Setup request without access token
        request = DummyRequest(json_body={})

        # Create API instance
        api = FullscriptAPI(event=DummyEvent())
        api.request = request

        result = api.create_session_grant()

        # Verify error response
        assert len(result) == 1
        response = result[0]
        assert response.status_code == HTTPStatus.BAD_REQUEST

        data = json.loads(response.content.decode())
        assert "error" in data
        assert data["error"] == "Missing access token"

    def test_create_session_grant_failure(self):
        """Test session grant creation handles API failure."""
        # Setup request
        request = DummyRequest(json_body={
            "access_token": "invalid_token"
        })

        # Create API instance
        api = FullscriptAPI(event=DummyEvent())
        api.request = request

        # Mock requests.post with failure
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"

        with patch("fullscript.api.fullscriptAPI.requests.post", return_value=mock_response):
            result = api.create_session_grant()

        # Verify error response
        assert len(result) == 1
        response = result[0]
        assert response.status_code == HTTPStatus.BAD_GATEWAY

        data = json.loads(response.content.decode())
        assert "error" in data

    # ==================== get_or_create_patient tests ====================

    def test_get_patient_with_existing_fullscript_id(self):
        """Test getting patient with existing Fullscript external identifier."""
        # Setup request
        request = DummyRequest(json_body={
            "access_token": "valid_access_token",
            "patient_id": "patient-123"
        })

        # Create API instance
        api = FullscriptAPI(event=DummyEvent())
        api.request = request

        # Mock Patient
        mock_patient = Mock()
        mock_patient.id = "patient-123"
        mock_external_identifiers = Mock()
        mock_external_identifiers.filter.return_value.values_list.return_value.last.return_value = "fullscript-patient-456"
        mock_patient.external_identifiers = mock_external_identifiers

        with patch("fullscript.api.fullscriptAPI.Patient") as mock_patient_class:
            mock_patient_class.objects.get.return_value = mock_patient

            result = api.get_or_create_patient()

        # Verify response returns existing Fullscript ID
        assert len(result) == 1
        response = result[0]
        assert response.status_code == HTTPStatus.OK

        data = json.loads(response.content.decode())
        assert data["id"] == "fullscript-patient-456"

    def test_create_patient_without_fullscript_id(self):
        """Test creating patient in Fullscript when external identifier doesn't exist."""
        # Setup request
        request = DummyRequest(json_body={
            "access_token": "valid_access_token",
            "patient_id": "patient-123"
        })

        # Create API instance
        api = FullscriptAPI(event=DummyEvent())
        api.request = request

        # Mock Patient without Fullscript ID
        mock_patient = Mock()
        mock_patient.id = "patient-123"
        mock_patient.first_name = "John"
        mock_patient.last_name = "Doe"

        # Mock telecom for email
        mock_telecom = Mock()
        mock_email = Mock()
        mock_email.value = "john.doe@example.com"
        mock_telecom.filter.return_value.first.return_value = mock_email
        mock_telecom.filter.return_value.exists.return_value = True
        mock_patient.telecom = mock_telecom

        mock_external_identifiers = Mock()
        mock_external_identifiers.filter.return_value.values_list.return_value.last.return_value = None
        mock_patient.external_identifiers = mock_external_identifiers

        # Mock Fullscript API response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "patient": {
                "id": "fullscript-patient-789"
            }
        }

        with patch("fullscript.api.fullscriptAPI.Patient") as mock_patient_class:
            mock_patient_class.objects.get.return_value = mock_patient
            with patch("fullscript.api.fullscriptAPI.requests.post", return_value=mock_response):
                with patch("fullscript.api.fullscriptAPI.CreatePatientExternalIdentifier") as mock_create_identifier:
                    mock_effect = Mock()
                    mock_effect.create.return_value = Mock()
                    mock_create_identifier.return_value = mock_effect

                    result = api.get_or_create_patient()

        # Verify response contains new patient ID and effect
        assert len(result) == 2
        response = result[1]  # Second item is the Response
        assert response.status_code == HTTPStatus.OK

        data = json.loads(response.content.decode())
        assert data["id"] == "fullscript-patient-789"

    def test_get_or_create_patient_api_failure(self):
        """Test patient creation handles Fullscript API failure."""
        # Setup request
        request = DummyRequest(json_body={
            "access_token": "valid_access_token",
            "patient_id": "patient-123"
        })

        # Create API instance
        api = FullscriptAPI(event=DummyEvent())
        api.request = request

        # Mock Patient without Fullscript ID
        mock_patient = Mock()
        mock_patient.id = "patient-123"
        mock_patient.first_name = "John"
        mock_patient.last_name = "Doe"

        mock_telecom = Mock()
        mock_email = Mock()
        mock_email.value = "john.doe@example.com"
        mock_telecom.filter.return_value.first.return_value = mock_email
        mock_telecom.filter.return_value.exists.return_value = True
        mock_patient.telecom = mock_telecom

        mock_external_identifiers = Mock()
        mock_external_identifiers.filter.return_value.values_list.return_value.last.return_value = None
        mock_patient.external_identifiers = mock_external_identifiers

        # Mock Fullscript API failure
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Email already exists"

        with patch("fullscript.api.fullscriptAPI.Patient") as mock_patient_class:
            mock_patient_class.objects.get.return_value = mock_patient
            with patch("fullscript.api.fullscriptAPI.requests.post", return_value=mock_response):
                result = api.get_or_create_patient()

        # Verify error response
        assert len(result) == 1
        response = result[0]
        assert response.status_code == HTTPStatus.BAD_GATEWAY

    # ==================== treatment_plan_created tests ====================

    def test_treatment_plan_created_success(self):
        """Test processing treatment plan with valid recommendations."""
        # Setup request
        request = DummyRequest(json_body={
            "patient_id": "patient-123",
            "treatment": {
                "data": {
                    "treatmentPlan": {
                        "recommendations": [
                            {
                                "variantId": "variant-456",
                                "dosage": {
                                    "recommendedAmount": "2 capsules",
                                    "recommendedFrequency": "twice daily",
                                    "recommendedDuration": "30 days",
                                    "format": "capsule"
                                },
                                "refill": True
                            }
                        ]
                    }
                }
            }
        })

        # Create API instance
        api = FullscriptAPI(event=DummyEvent())
        api.request = request

        # Mock Staff
        mock_staff_objects = Mock()
        mock_staff_objects.values_list.return_value.get.return_value = "staff-123"

        # Mock cache with access token
        mock_cache = Mock()
        mock_cache.get.return_value = {
            "access_token": "valid_access_token"
        }

        # Mock Patient with note
        mock_patient = Mock()
        mock_patient.id = "patient-123"
        mock_note = Mock()
        mock_note.id = "note-789"
        mock_patient.notes.last.return_value = mock_note
        mock_patient.notes.exists.return_value = True

        # Mock Fullscript variant response
        mock_variant_response = Mock()
        mock_variant_response.status_code = 200
        mock_variant_response.json.return_value = {
            "variant": {
                "sku": "VIT-D3-1000",
                "product": {
                    "name": "Vitamin D3 1000 IU"
                }
            }
        }

        with patch("fullscript.api.fullscriptAPI.Staff") as mock_staff:
            mock_staff.objects = mock_staff_objects
            with patch("fullscript.api.fullscriptAPI.get_cache", return_value=mock_cache):
                with patch("fullscript.api.fullscriptAPI.Patient") as mock_patient_class:
                    mock_patient_class.objects.get.return_value = mock_patient
                    with patch("fullscript.api.fullscriptAPI.requests.get", return_value=mock_variant_response):
                        with patch("fullscript.api.fullscriptAPI.MedicationStatementCommand") as mock_med_command:
                            mock_command = Mock()
                            mock_command.originate.return_value = Mock()
                            mock_med_command.return_value = mock_command

                            api.request.headers = {"canvas-logged-in-user-id": "staff-123"}

                            result = api.treatment_plan_created()

        # Verify response includes medication command and success response
        assert len(result) == 2  # 1 medication + 1 success response
        response = result[-1]  # Last item is the Response
        assert response.status_code == HTTPStatus.OK

        data = json.loads(response.content.decode())
        assert data["status"] == "ok"

    def test_treatment_plan_created_no_recommendations(self):
        """Test treatment plan with no recommendations returns error."""
        # Setup request with empty recommendations
        request = DummyRequest(json_body={
            "patient_id": "patient-123",
            "treatment": {
                "data": {
                    "treatmentPlan": {
                        "recommendations": []
                    }
                }
            }
        })

        # Create API instance
        api = FullscriptAPI(event=DummyEvent())
        api.request = request

        # Mock Staff
        mock_staff_objects = Mock()
        mock_staff_objects.values_list.return_value.get.return_value = "staff-123"

        # Mock cache (needed even though not used, to avoid plugin context error)
        mock_cache = Mock()

        with patch("fullscript.api.fullscriptAPI.Staff") as mock_staff:
            mock_staff.objects = mock_staff_objects
            with patch("fullscript.api.fullscriptAPI.get_cache", return_value=mock_cache):
                api.request.headers = {"canvas-logged-in-user-id": "staff-123"}

                result = api.treatment_plan_created()

        # Verify error response
        assert len(result) == 1
        response = result[0]
        assert response.status_code == HTTPStatus.BAD_REQUEST

        data = json.loads(response.content.decode())
        assert "error" in data

    def test_treatment_plan_created_no_cached_token(self):
        """Test treatment plan processing without cached token."""
        # Setup request
        request = DummyRequest(json_body={
            "patient_id": "patient-123",
            "treatment": {
                "data": {
                    "treatmentPlan": {
                        "recommendations": [{"variantId": "variant-456"}]
                    }
                }
            }
        })

        # Create API instance
        api = FullscriptAPI(event=DummyEvent())
        api.request = request

        # Mock Staff
        mock_staff_objects = Mock()
        mock_staff_objects.values_list.return_value.get.return_value = "staff-123"

        # Mock cache with no token
        mock_cache = Mock()
        mock_cache.get.return_value = None

        with patch("fullscript.api.fullscriptAPI.Staff") as mock_staff:
            mock_staff.objects = mock_staff_objects
            with patch("fullscript.api.fullscriptAPI.get_cache", return_value=mock_cache):
                api.request.headers = {"canvas-logged-in-user-id": "staff-123"}

                result = api.treatment_plan_created()

        # Verify error response
        assert len(result) == 1
        response = result[0]
        assert response.status_code == HTTPStatus.UNAUTHORIZED

        data = json.loads(response.content.decode())
        assert "error" in data

    def test_treatment_plan_created_no_note(self):
        """Test treatment plan processing when patient has no notes."""
        # Setup request
        request = DummyRequest(json_body={
            "patient_id": "patient-123",
            "treatment": {
                "data": {
                    "treatmentPlan": {
                        "recommendations": [{"variantId": "variant-456"}]
                    }
                }
            }
        })

        # Create API instance
        api = FullscriptAPI(event=DummyEvent())
        api.request = request

        # Mock Staff
        mock_staff_objects = Mock()
        mock_staff_objects.values_list.return_value.get.return_value = "staff-123"

        # Mock cache
        mock_cache = Mock()
        mock_cache.get.return_value = {"access_token": "token"}

        # Mock Patient without notes
        mock_patient = Mock()
        mock_patient.id = "patient-123"
        mock_patient.notes.exists.return_value = False
        mock_patient.notes.last.return_value = None

        with patch("fullscript.api.fullscriptAPI.Staff") as mock_staff:
            mock_staff.objects = mock_staff_objects
            with patch("fullscript.api.fullscriptAPI.get_cache", return_value=mock_cache):
                with patch("fullscript.api.fullscriptAPI.Patient") as mock_patient_class:
                    mock_patient_class.objects.get.return_value = mock_patient

                    api.request.headers = {"canvas-logged-in-user-id": "staff-123"}

                    result = api.treatment_plan_created()

        # Verify error response
        assert len(result) == 1
        response = result[0]
        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR

        data = json.loads(response.content.decode())
        assert "error" in data