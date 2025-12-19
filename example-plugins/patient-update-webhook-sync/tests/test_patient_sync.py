import json
from unittest.mock import Mock, patch

import pytest

from canvas_sdk.effects import EffectType
from canvas_sdk.events import EventType


@pytest.fixture
def mock_event() -> Mock:
    """Create a mock PATIENT_UPDATED event."""
    event = Mock()
    event.type = EventType.PATIENT_UPDATED
    # Create a mock target with an id attribute
    target = Mock()
    target.id = "patient-123"
    event.target = target
    return event


@pytest.fixture
def mock_http_response() -> Mock:
    """Create a mock successful HTTP response."""
    response = Mock()
    response.status_code = 200
    response.text = "Success"
    return response


@pytest.fixture
def mock_http_error_response() -> Mock:
    """Create a mock failed HTTP response."""
    response = Mock()
    response.status_code = 500
    response.text = "Internal Server Error"
    return response


@pytest.fixture
def full_secrets() -> dict[str, str]:
    """Return all required secrets."""
    return {
        "PARTNER_WEBHOOK_URL": "https://partner.example.com/webhook",
        "PARTNER_API_KEY": "partner-api-key-123",
        "SLACK_ENDPOINT_URL": "https://slack.example.com/webhook",
        "SLACK_API_KEY": "slack-api-key-456",
    }


def test_webhook_headers_includes_api_key(mock_event: Mock, full_secrets: dict[str, str]) -> None:
    """Test that webhook headers include the API key."""
    from patient_update_webhook_sync.handlers.patient_webhook_sync import PatientSync

    protocol = PatientSync(event=mock_event, secrets=full_secrets)
    headers = protocol.webhook_headers
    assert headers["X-API-Key"] == "partner-api-key-123"
    assert headers["Content-Type"] == "application/json"


def test_slack_headers_includes_bearer_token(
    mock_event: Mock, full_secrets: dict[str, str]
) -> None:
    """Test that Slack headers include Bearer token."""
    from patient_update_webhook_sync.handlers.patient_webhook_sync import PatientSync

    protocol = PatientSync(event=mock_event, secrets=full_secrets)
    headers = protocol.slack_headers
    assert headers["Authorization"] == "Bearer slack-api-key-456"
    assert headers["Content-Type"] == "application/json"


def test_compute_returns_empty_when_no_webhook_url(mock_event: Mock) -> None:
    """Test that compute returns empty list when webhook URL is not configured."""
    from patient_update_webhook_sync.handlers.patient_webhook_sync import PatientSync

    protocol = PatientSync(event=mock_event, secrets={})
    effects = protocol.compute()
    assert effects == []


def test_compute_returns_empty_when_no_webhook_api_key(mock_event: Mock) -> None:
    """Test that compute returns empty list when webhook API key is not configured."""
    from patient_update_webhook_sync.handlers.patient_webhook_sync import PatientSync

    secrets = {"PARTNER_WEBHOOK_URL": "https://partner.example.com/webhook"}
    protocol = PatientSync(event=mock_event, secrets=secrets)
    effects = protocol.compute()
    assert effects == []


@patch("patient_update_webhook_sync.handlers.patient_webhook_sync.Http")
def test_compute_succeeds_with_200_response(
    mock_http_class: Mock, mock_event: Mock, full_secrets: dict[str, str], mock_http_response: Mock
) -> None:
    """Test successful webhook call with 200 status code."""
    from patient_update_webhook_sync.handlers.patient_webhook_sync import PatientSync

    mock_http = Mock()
    mock_http.post.return_value = mock_http_response
    mock_http_class.return_value = mock_http

    protocol = PatientSync(event=mock_event, secrets=full_secrets)
    effects = protocol.compute()

    # Verify webhook was called with correct parameters
    mock_http.post.assert_called_once()
    call_args = mock_http.post.call_args
    assert call_args.kwargs["json"]["canvas_patient_id"] == "patient-123"
    assert call_args.args[0] == "https://partner.example.com/webhook"

    # Verify success log effect
    assert len(effects) == 1
    assert effects[0].type == EffectType.LOG
    log_data = json.loads(effects[0].payload)
    assert log_data["event"] == "webhook_success"
    assert log_data["patient_id"] == "patient-123"
    assert log_data["status_code"] == 200


@patch("patient_update_webhook_sync.handlers.patient_webhook_sync.Http")
def test_compute_handles_connection_error_with_slack(
    mock_http_class: Mock, mock_event: Mock, full_secrets: dict[str, str]
) -> None:
    """Test handling of connection error with Slack notification."""
    from patient_update_webhook_sync.handlers.patient_webhook_sync import PatientSync

    mock_http = Mock()
    mock_http.post.side_effect = [
        ConnectionError("Connection refused"),  # First call fails
        Mock(),  # Slack notification succeeds
    ]
    mock_http_class.return_value = mock_http

    protocol = PatientSync(event=mock_event, secrets=full_secrets)
    effects = protocol.compute()

    # Verify webhook was attempted
    assert mock_http.post.call_count == 2  # Webhook attempt + Slack notification

    # Verify Slack notification was sent
    slack_call = mock_http.post.call_args_list[1]
    assert slack_call.args[0] == "https://slack.example.com/webhook"
    slack_message = slack_call.kwargs["json"]
    assert "Patient update webhook failed" in slack_message["text"]
    assert "patient-123" in slack_message["text"]

    # Verify error log effect
    assert len(effects) == 1
    assert effects[0].type == EffectType.LOG
    log_data = json.loads(effects[0].payload)
    assert log_data["event"] == "webhook_connection_error"
    assert log_data["patient_id"] == "patient-123"
    assert "Connection refused" in log_data["error"]


@patch("patient_update_webhook_sync.handlers.patient_webhook_sync.Http")
def test_compute_handles_connection_error_without_slack(
    mock_http_class: Mock, mock_event: Mock
) -> None:
    """Test handling of connection error without Slack configured."""
    from patient_update_webhook_sync.handlers.patient_webhook_sync import PatientSync

    secrets = {
        "PARTNER_WEBHOOK_URL": "https://partner.example.com/webhook",
        "PARTNER_API_KEY": "partner-api-key-123",
    }
    mock_http = Mock()
    mock_http.post.side_effect = ConnectionError("Connection refused")
    mock_http_class.return_value = mock_http

    protocol = PatientSync(event=mock_event, secrets=secrets)
    effects = protocol.compute()

    # Verify only webhook was attempted (no Slack notification)
    assert mock_http.post.call_count == 1

    # Verify error log effect
    assert len(effects) == 1
    assert effects[0].type == EffectType.LOG
    log_data = json.loads(effects[0].payload)
    assert log_data["event"] == "webhook_connection_error"
    assert log_data["patient_id"] == "patient-123"


@patch("patient_update_webhook_sync.handlers.patient_webhook_sync.Http")
def test_compute_handles_non_200_response_with_slack(
    mock_http_class: Mock,
    mock_event: Mock,
    full_secrets: dict[str, str],
    mock_http_error_response: Mock,
) -> None:
    """Test handling of non-200 response with Slack notification."""
    from patient_update_webhook_sync.handlers.patient_webhook_sync import PatientSync

    mock_http = Mock()
    mock_http.post.side_effect = [
        mock_http_error_response,  # Webhook fails with 500
        Mock(),  # Slack notification succeeds
    ]
    mock_http_class.return_value = mock_http

    protocol = PatientSync(event=mock_event, secrets=full_secrets)
    effects = protocol.compute()

    # Verify webhook was called and Slack notification sent
    assert mock_http.post.call_count == 2

    # Verify Slack notification includes status code
    slack_call = mock_http.post.call_args_list[1]
    slack_message = slack_call.kwargs["json"]
    assert "500" in str(slack_message["blocks"][0]["text"]["text"])

    # Verify error log effect
    assert len(effects) == 1
    assert effects[0].type == EffectType.LOG
    log_data = json.loads(effects[0].payload)
    assert log_data["event"] == "webhook_failure"
    assert log_data["patient_id"] == "patient-123"
    assert log_data["status_code"] == 500
    assert log_data["error"] == "Internal Server Error"


@patch("patient_update_webhook_sync.handlers.patient_webhook_sync.Http")
def test_compute_handles_non_200_response_without_slack(
    mock_http_class: Mock, mock_event: Mock, mock_http_error_response: Mock
) -> None:
    """Test handling of non-200 response without Slack configured."""
    from patient_update_webhook_sync.handlers.patient_webhook_sync import PatientSync

    secrets = {
        "PARTNER_WEBHOOK_URL": "https://partner.example.com/webhook",
        "PARTNER_API_KEY": "partner-api-key-123",
    }
    mock_http = Mock()
    mock_http.post.return_value = mock_http_error_response
    mock_http_class.return_value = mock_http

    protocol = PatientSync(event=mock_event, secrets=secrets)
    effects = protocol.compute()

    # Verify only webhook was called (no Slack notification)
    assert mock_http.post.call_count == 1

    # Verify error log effect
    assert len(effects) == 1
    assert effects[0].type == EffectType.LOG
    log_data = json.loads(effects[0].payload)
    assert log_data["event"] == "webhook_failure"


def test_send_slack_notification_skips_when_no_url(mock_event: Mock) -> None:
    """Test that Slack notification is skipped when URL is not configured."""
    from patient_update_webhook_sync.handlers.patient_webhook_sync import PatientSync

    secrets = {"SLACK_API_KEY": "slack-api-key-456"}
    protocol = PatientSync(event=mock_event, secrets=secrets)

    mock_http = Mock()
    protocol._send_slack_notification(mock_http, "patient-123", "Test error")

    # Verify no HTTP call was made
    mock_http.post.assert_not_called()


def test_send_slack_notification_skips_when_no_api_key(mock_event: Mock) -> None:
    """Test that Slack notification is skipped when API key is not configured."""
    from patient_update_webhook_sync.handlers.patient_webhook_sync import PatientSync

    secrets = {"SLACK_ENDPOINT_URL": "https://slack.example.com/webhook"}
    protocol = PatientSync(event=mock_event, secrets=secrets)

    mock_http = Mock()
    protocol._send_slack_notification(mock_http, "patient-123", "Test error")

    # Verify no HTTP call was made
    mock_http.post.assert_not_called()


def test_send_slack_notification_includes_status_code(
    mock_event: Mock, full_secrets: dict[str, str]
) -> None:
    """Test that Slack notification includes status code when provided."""
    from patient_update_webhook_sync.handlers.patient_webhook_sync import PatientSync

    protocol = PatientSync(event=mock_event, secrets=full_secrets)

    mock_http = Mock()
    protocol._send_slack_notification(mock_http, "patient-123", "Server error", status_code=500)

    # Verify Slack was called with correct message
    mock_http.post.assert_called_once()
    call_args = mock_http.post.call_args
    message = call_args.kwargs["json"]

    text_content = message["blocks"][0]["text"]["text"]
    assert "patient-123" in text_content
    assert "500" in text_content
    assert "Server error" in text_content


def test_send_slack_notification_without_status_code(
    mock_event: Mock, full_secrets: dict[str, str]
) -> None:
    """Test that Slack notification works without status code."""
    from patient_update_webhook_sync.handlers.patient_webhook_sync import PatientSync

    protocol = PatientSync(event=mock_event, secrets=full_secrets)

    mock_http = Mock()
    protocol._send_slack_notification(mock_http, "patient-123", "Connection error")

    # Verify Slack was called with correct message
    mock_http.post.assert_called_once()
    call_args = mock_http.post.call_args
    message = call_args.kwargs["json"]

    text_content = message["blocks"][0]["text"]["text"]
    assert "patient-123" in text_content
    assert "Connection error" in text_content
    assert "Webhook Status" not in text_content  # Should not include status when not provided


def test_send_slack_notification_truncates_long_error(
    mock_event: Mock, full_secrets: dict[str, str]
) -> None:
    """Test that Slack notification truncates error messages longer than 500 chars."""
    from patient_update_webhook_sync.handlers.patient_webhook_sync import PatientSync

    protocol = PatientSync(event=mock_event, secrets=full_secrets)

    long_error = "Error: " + "X" * 600  # Create 600+ character error
    mock_http = Mock()
    protocol._send_slack_notification(mock_http, "patient-123", long_error)

    # Verify error was truncated
    call_args = mock_http.post.call_args
    message = call_args.kwargs["json"]
    text_content = message["blocks"][0]["text"]["text"]

    # Error should be truncated to 500 chars
    truncated_error = long_error[:500]
    assert truncated_error in text_content
    assert len(truncated_error) == 500
