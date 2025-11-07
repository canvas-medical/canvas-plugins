"""Comprehensive tests for email_bounce plugin."""

from unittest.mock import Mock, patch

import arrow
import pytest
from api_samples.routes.email_bounce import EmailBounceAPI

from canvas_sdk.effects.simple_api import JSONResponse
from canvas_sdk.effects.task import AddTask, TaskStatus
from canvas_sdk.handlers.simple_api import APIKeyCredentials
from canvas_sdk.v1.data import Patient


class DummyRequest:
    """A dummy request object for testing EmailBounceAPI."""

    def __init__(self, json_body=None):
        self._json_body = json_body or {}

    def json(self):
        """Return the mocked JSON body."""
        return self._json_body


class DummyEvent:
    """A dummy event object for testing API handlers."""

    def __init__(self, context=None):
        self.context = context or {}


def test_import_email_bounce_api():
    """Test that EmailBounceAPI can be imported without errors."""
    # Verify the class exists and has expected attributes
    assert EmailBounceAPI is not None
    assert hasattr(EmailBounceAPI, "PATH")
    assert hasattr(EmailBounceAPI, "post")


def test_email_bounce_api_configuration():
    """Test that EmailBounceAPI has correct path configuration."""
    # Verify PATH is configured
    assert EmailBounceAPI.PATH == "/crm-webhooks/email-bounce"


class TestEmailBounceAPI:
    """Test suite for EmailBounceAPI endpoint."""

    def test_authenticate_with_valid_key(self):
        """Test authentication succeeds with valid API key."""
        dummy_context = {"method": "POST", "path": "/crm-webhooks/email-bounce"}
        api = EmailBounceAPI(event=DummyEvent(context=dummy_context))  # type: ignore[arg-type]
        api.secrets = {"my-api-key": "valid-secret-key"}

        # Create mock credentials
        mock_credentials = Mock(spec=APIKeyCredentials)
        mock_credentials.key = "valid-secret-key"

        assert api.authenticate(mock_credentials) is True

    def test_authenticate_with_invalid_key(self):
        """Test authentication fails with invalid API key."""
        dummy_context = {"method": "POST", "path": "/crm-webhooks/email-bounce"}
        api = EmailBounceAPI(event=DummyEvent(context=dummy_context))  # type: ignore[arg-type]
        api.secrets = {"my-api-key": "valid-secret-key"}

        # Create mock credentials
        mock_credentials = Mock(spec=APIKeyCredentials)
        mock_credentials.key = "wrong-key"

        assert api.authenticate(mock_credentials) is False

    def test_post_creates_task_for_valid_mrn(self):
        """Test POST endpoint creates task with correct parameters for valid MRN."""
        # Create mock patient
        mock_patient = Mock(spec=Patient)
        mock_patient.id = "123"
        mock_patient.mrn = "TEST-MRN-001"

        # Create API request
        request = DummyRequest(json_body={"mrn": "TEST-MRN-001"})

        # Create API instance with proper context
        dummy_context = {"method": "POST", "path": "/crm-webhooks/email-bounce"}
        api = EmailBounceAPI(event=DummyEvent(context=dummy_context))  # type: ignore[arg-type]
        api.request = request  # type: ignore[attr-defined]

        # Mock Patient.objects.get
        with patch.object(Patient.objects, "get", return_value=mock_patient):
            # Mock arrow.utcnow to have predictable datetime
            mock_now = arrow.get("2025-01-01T12:00:00Z")

            with patch("api_samples.routes.email_bounce.arrow.utcnow", return_value=mock_now):
                with patch.object(AddTask, "apply") as mock_apply:
                    mock_apply.return_value = Mock()

                    result = api.post()

                    # Verify result contains two items: task effect and JSON response
                    assert len(result) == 2

                    # Verify AddTask.apply was called
                    mock_apply.assert_called_once()

                    # Verify JSON response
                    assert isinstance(result[1], JSONResponse)
                    assert result[1].content == b'{"message": "Task Created"}'

    def test_post_creates_task_with_correct_parameters(self):
        """Test POST endpoint creates AddTask effect with correct parameters."""
        # Create mock patient
        mock_patient = Mock(spec=Patient)
        mock_patient.id = "456"
        mock_patient.mrn = "PATIENT-123"

        # Create API request
        request = DummyRequest(json_body={"mrn": "PATIENT-123"})

        # Create API instance
        dummy_context = {"method": "POST", "path": "/crm-webhooks/email-bounce"}
        api = EmailBounceAPI(event=DummyEvent(context=dummy_context))  # type: ignore[arg-type]
        api.request = request  # type: ignore[attr-defined]

        # Mock Patient.objects.get
        with patch.object(Patient.objects, "get", return_value=mock_patient):
            # Mock arrow.utcnow
            mock_now = arrow.get("2025-02-15T10:30:00Z")
            expected_due = mock_now.shift(days=5).datetime

            with patch("api_samples.routes.email_bounce.arrow.utcnow", return_value=mock_now):
                with patch("api_samples.routes.email_bounce.AddTask") as mock_add_task_class:
                    mock_task_instance = Mock()
                    mock_task_instance.apply.return_value = Mock()
                    mock_add_task_class.return_value = mock_task_instance

                    result = api.post()

                    # Verify AddTask was instantiated with correct parameters
                    mock_add_task_class.assert_called_once_with(
                        patient_id="456",
                        title="Please confirm contact information.",
                        due=expected_due,
                        status=TaskStatus.OPEN,
                        labels=["CRM"],
                    )

    def test_post_with_nonexistent_patient(self):
        """Test POST endpoint raises exception when patient MRN not found."""
        # Create API request
        request = DummyRequest(json_body={"mrn": "NONEXISTENT-MRN"})

        # Create API instance
        dummy_context = {"method": "POST", "path": "/crm-webhooks/email-bounce"}
        api = EmailBounceAPI(event=DummyEvent(context=dummy_context))  # type: ignore[arg-type]
        api.request = request  # type: ignore[attr-defined]

        # Mock Patient.objects.get to raise DoesNotExist
        with patch.object(Patient.objects, "get", side_effect=Patient.DoesNotExist):
            with pytest.raises(Patient.DoesNotExist):
                api.post()

    def test_post_with_missing_mrn_key(self):
        """Test POST endpoint raises KeyError when 'mrn' key is missing from JSON."""
        # Create API request with missing mrn key
        request = DummyRequest(json_body={"wrong_key": "some-value"})

        # Create API instance
        dummy_context = {"method": "POST", "path": "/crm-webhooks/email-bounce"}
        api = EmailBounceAPI(event=DummyEvent(context=dummy_context))  # type: ignore[arg-type]
        api.request = request  # type: ignore[attr-defined]

        with pytest.raises(KeyError):
            api.post()
