"""Tests for resolve_namespace_secret and verify_plugin_namespace_access.

Tests cover:
1. resolve_namespace_secret — secret name mapping and retrieval
2. verify_plugin_namespace_access — orchestrator for namespace verification
"""

from unittest.mock import MagicMock, patch

import pytest

from plugin_runner.exceptions import NamespaceAccessError
from plugin_runner.plugin_runner import (
    CustomData,
    resolve_namespace_secret,
    verify_plugin_namespace_access,
)

# ===========================================================================
# Tests for resolve_namespace_secret
# ===========================================================================


def test_resolve_returns_value_for_read_access() -> None:
    """Read access should use 'read_access_key' and return its value."""
    secrets = {"namespace_read_access_key": "my-read-secret"}

    result = resolve_namespace_secret("my_plugin", "my_ns", "read", secrets)

    assert result == "my-read-secret"


def test_resolve_returns_value_for_read_write_access() -> None:
    """Read-write access should use 'read_write_access_key' and return its value."""
    secrets = {"namespace_read_write_access_key": "my-rw-secret"}

    result = resolve_namespace_secret("my_plugin", "my_ns", "read_write", secrets)

    assert result == "my-rw-secret"


def test_resolve_raises_when_secret_missing() -> None:
    """Should raise NamespaceAccessError when the secret key is not in secrets_json."""
    secrets: dict[str, str] = {}

    with pytest.raises(NamespaceAccessError):
        resolve_namespace_secret("my_plugin", "my_ns", "read", secrets)


def test_resolve_raises_when_secret_empty() -> None:
    """Should raise NamespaceAccessError when the secret value is an empty string."""
    secrets = {"namespace_read_access_key": ""}

    with pytest.raises(NamespaceAccessError):
        resolve_namespace_secret("my_plugin", "my_ns", "read", secrets)


def test_resolve_error_message_includes_context() -> None:
    """Error message should mention plugin name, namespace, and secret name."""
    secrets: dict[str, str] = {}

    with pytest.raises(NamespaceAccessError, match="my_plugin") as exc_info:
        resolve_namespace_secret("my_plugin", "org__data", "read", secrets)

    message = str(exc_info.value)
    assert "org__data" in message
    assert "namespace_read_access_key" in message


# ===========================================================================
# Tests for verify_plugin_namespace_access
# ===========================================================================


@patch("plugin_runner.installation.check_namespace_auth_key", return_value="read")
def test_returns_config_on_success(mock_verify: MagicMock) -> None:
    """Happy path: should return namespace config dict."""
    custom_data: CustomData = {"namespace": "org__data", "access": "read"}
    secrets = {"namespace_read_access_key": "valid-key"}

    result = verify_plugin_namespace_access("my_plugin", custom_data, secrets)

    assert result == {"namespace": "org__data", "access_level": "read"}
    mock_verify.assert_called_once_with("org__data", "valid-key")


def test_raises_for_missing_secret() -> None:
    """Should propagate NamespaceAccessError from resolve_namespace_secret."""
    custom_data: CustomData = {"namespace": "org__data", "access": "read"}
    secrets: dict[str, str] = {}

    with pytest.raises(NamespaceAccessError, match="not configured"):
        verify_plugin_namespace_access("my_plugin", custom_data, secrets)


@patch("plugin_runner.installation.check_namespace_auth_key", return_value=None)
def test_raises_for_invalid_key(mock_verify: MagicMock) -> None:
    """Should raise NamespaceAccessError when the key is not recognized."""
    custom_data: CustomData = {"namespace": "org__data", "access": "read"}
    secrets = {"namespace_read_access_key": "bad-key"}

    with pytest.raises(NamespaceAccessError, match="not a valid access key"):
        verify_plugin_namespace_access("my_plugin", custom_data, secrets)


@patch("plugin_runner.installation.check_namespace_auth_key", return_value="read")
def test_raises_for_insufficient_access(mock_verify: MagicMock) -> None:
    """Should raise when read_write requested but only read granted."""
    custom_data: CustomData = {"namespace": "org__data", "access": "read_write"}
    secrets = {"namespace_read_write_access_key": "valid-key"}

    with pytest.raises(NamespaceAccessError, match="only grants 'read' access"):
        verify_plugin_namespace_access("my_plugin", custom_data, secrets)


@patch("plugin_runner.installation.check_namespace_auth_key", return_value="read_write")
def test_read_access_accepted_with_read_write_grant(mock_verify: MagicMock) -> None:
    """Read access should succeed even when the key grants read_write."""
    custom_data: CustomData = {"namespace": "org__data", "access": "read"}
    secrets = {"namespace_read_access_key": "valid-key"}

    result = verify_plugin_namespace_access("my_plugin", custom_data, secrets)

    assert result == {"namespace": "org__data", "access_level": "read"}


@patch("plugin_runner.plugin_runner.sentry_sdk")
@patch(
    "plugin_runner.installation.check_namespace_auth_key",
    side_effect=RuntimeError("db connection failed"),
)
def test_wraps_unexpected_exceptions(mock_verify: MagicMock, mock_sentry: MagicMock) -> None:
    """Unexpected exceptions should be wrapped in NamespaceAccessError with __cause__."""
    custom_data: CustomData = {"namespace": "org__data", "access": "read"}
    secrets = {"namespace_read_access_key": "valid-key"}

    with pytest.raises(NamespaceAccessError, match="Unexpected error") as exc_info:
        verify_plugin_namespace_access("my_plugin", custom_data, secrets)

    assert isinstance(exc_info.value.__cause__, RuntimeError)


@patch("plugin_runner.plugin_runner.sentry_sdk")
@patch(
    "plugin_runner.installation.check_namespace_auth_key",
    side_effect=RuntimeError("db connection failed"),
)
def test_propagates_namespace_access_error_unchanged(
    mock_verify: MagicMock, mock_sentry: MagicMock
) -> None:
    """NamespaceAccessError from resolve_namespace_secret should not be double-wrapped."""
    custom_data: CustomData = {"namespace": "org__data", "access": "read"}
    # Missing secret triggers NamespaceAccessError in resolve_namespace_secret
    secrets: dict[str, str] = {}

    with pytest.raises(NamespaceAccessError, match="not configured"):
        verify_plugin_namespace_access("my_plugin", custom_data, secrets)

    # Should NOT have reported to sentry — it's an expected error type
    mock_sentry.capture_exception.assert_not_called()


@patch("plugin_runner.plugin_runner.sentry_sdk")
@patch("plugin_runner.plugin_runner.log")
@patch(
    "plugin_runner.installation.check_namespace_auth_key",
    side_effect=RuntimeError("db connection failed"),
)
def test_logs_and_reports_unexpected_exceptions(
    mock_verify: MagicMock, mock_log: MagicMock, mock_sentry: MagicMock
) -> None:
    """Unexpected exceptions should be logged and reported to Sentry."""
    custom_data: CustomData = {"namespace": "org__data", "access": "read"}
    secrets = {"namespace_read_access_key": "valid-key"}

    with pytest.raises(NamespaceAccessError):
        verify_plugin_namespace_access("my_plugin", custom_data, secrets)

    mock_log.exception.assert_called_once()
    mock_sentry.capture_exception.assert_called_once()
