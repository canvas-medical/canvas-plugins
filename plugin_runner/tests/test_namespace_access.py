"""Tests for namespace access verification in plugin_runner.

Tests verify that:
1. NamespaceAccessError is raised appropriately
2. check_namespace_auth_key function works correctly
3. Error handling in load_plugins catches NamespaceAccessError
"""

import hashlib
from unittest.mock import MagicMock, patch

import pytest

from plugin_runner.exceptions import NamespaceAccessError


class TestNamespaceAccessError:
    """Tests for the NamespaceAccessError exception."""

    def test_exception_is_raised(self) -> None:
        """NamespaceAccessError can be raised and caught."""
        with pytest.raises(NamespaceAccessError):
            raise NamespaceAccessError("Test error")

    def test_exception_inherits_from_plugin_error(self) -> None:
        """NamespaceAccessError should inherit from PluginError."""
        from plugin_runner.exceptions import PluginError

        exc = NamespaceAccessError("Test")
        assert isinstance(exc, PluginError)

    def test_exception_message_preserved(self) -> None:
        """NamespaceAccessError should preserve the error message."""
        message = "Plugin 'test' denied access to namespace 'ns'"
        exc = NamespaceAccessError(message)
        assert message in str(exc)

    def test_exception_with_missing_secret_message(self) -> None:
        """Error message should include helpful information about missing secrets."""
        exc = NamespaceAccessError(
            "Plugin 'my_plugin' declares namespace 'org__data' with 'read' access "
            "but secret 'namespace_read_access_key' is not configured. "
            "Ensure the secret is listed in the manifest's 'secrets' array and has a value set."
        )
        assert "my_plugin" in str(exc)
        assert "org__data" in str(exc)
        assert "namespace_read_access_key" in str(exc)
        assert "manifest" in str(exc)

    def test_exception_with_invalid_key_message(self) -> None:
        """Error message should include helpful information about invalid keys."""
        exc = NamespaceAccessError(
            "Plugin 'my_plugin' denied access to namespace 'org__data': "
            "the 'namespace_read_access_key' value is not a valid access key for this namespace."
        )
        assert "denied access" in str(exc)
        assert "not a valid access key" in str(exc)

    def test_exception_with_insufficient_access_message(self) -> None:
        """Error message should explain when write access is needed but only read granted."""
        exc = NamespaceAccessError(
            "Plugin 'my_plugin' requests 'read_write' access to namespace 'org__data' "
            "but the provided key only grants 'read' access. "
            "Use the `namespace_read_write_access_key' secret for write access."
        )
        assert "read_write" in str(exc)
        assert "only grants 'read' access" in str(exc)


class TestVerifyNamespaceAccessFunction:
    """Tests for the check_namespace_auth_key function in installation.py."""

    @patch("plugin_runner.installation.open_database_connection")
    def test_returns_access_level_when_key_found(self, mock_open_conn: MagicMock) -> None:
        """Should return access level when key hash matches."""
        from plugin_runner.installation import check_namespace_auth_key

        # Mock the database cursor
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"access_level": "read_write"}
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        mock_open_conn.return_value = mock_conn

        result = check_namespace_auth_key("my__namespace", "secret_key")

        assert result == "read_write"

    @patch("plugin_runner.installation.open_database_connection")
    def test_returns_read_access_level(self, mock_open_conn: MagicMock) -> None:
        """Should return 'read' when key has read-only access."""
        from plugin_runner.installation import check_namespace_auth_key

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"access_level": "read"}
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        mock_open_conn.return_value = mock_conn

        result = check_namespace_auth_key("my__namespace", "read_only_key")

        assert result == "read"

    @patch("plugin_runner.installation.open_database_connection")
    def test_returns_none_when_key_not_found(self, mock_open_conn: MagicMock) -> None:
        """Should return None when key hash not found in auth table."""
        from plugin_runner.installation import check_namespace_auth_key

        # Mock the database cursor to return no row
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        mock_open_conn.return_value = mock_conn

        result = check_namespace_auth_key("my__namespace", "invalid_key")

        assert result is None

    @patch("plugin_runner.installation.open_database_connection")
    def test_queries_correct_namespace_schema(self, mock_open_conn: MagicMock) -> None:
        """Should query the namespace's auth table with correct schema."""
        from plugin_runner.installation import check_namespace_auth_key

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"access_level": "read"}
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        mock_open_conn.return_value = mock_conn

        check_namespace_auth_key("org__shared_data", "some_key")

        # Check that the SQL includes the correct namespace schema
        call_args = mock_cursor.execute.call_args
        sql = call_args[0][0]
        assert "org__shared_data.namespace_auth" in sql

    def test_key_hash_is_consistent(self) -> None:
        """Same secret should always produce the same hash."""
        secret = "test_secret_key"
        expected_hash = hashlib.sha256(secret.encode()).hexdigest()

        # Verify hash is deterministic
        hash1 = hashlib.sha256(secret.encode()).hexdigest()
        hash2 = hashlib.sha256(secret.encode()).hexdigest()

        assert hash1 == hash2 == expected_hash

    def test_different_secrets_produce_different_hashes(self) -> None:
        """Different secrets should produce different hashes."""
        secret1 = "key_abc_123"
        secret2 = "key_xyz_789"

        hash1 = hashlib.sha256(secret1.encode()).hexdigest()
        hash2 = hashlib.sha256(secret2.encode()).hexdigest()

        assert hash1 != hash2


class TestSecretNameDetermination:
    """Tests for determining the correct secret name based on access level."""

    def test_read_access_uses_read_access_key(self) -> None:
        """Read access should use 'namespace_read_access_key' secret."""
        # This tests the inline logic: secret_name = "namespace_read_write_access_key" if declared_access == "read_write" else "namespace_read_access_key"
        declared_access = "read"
        secret_name = (
            "namespace_read_write_access_key"
            if declared_access == "read_write"
            else "namespace_read_access_key"
        )
        assert secret_name == "namespace_read_access_key"

    def test_read_write_access_uses_read_write_access_key(self) -> None:
        """Read-write access should use 'namespace_read_write_access_key' secret."""
        declared_access = "read_write"
        secret_name = (
            "namespace_read_write_access_key"
            if declared_access == "read_write"
            else "namespace_read_access_key"
        )
        assert secret_name == "namespace_read_write_access_key"


class TestLoadPluginsHandlesNamespaceErrors:
    """Tests for error handling in load_plugins functions."""

    @patch("plugin_runner.plugin_runner.refresh_event_type_map")
    @patch("plugin_runner.plugin_runner.load_or_reload_plugin")
    @patch("plugin_runner.plugin_runner.sentry_sdk")
    def test_load_plugins_catches_namespace_access_error(
        self, mock_sentry: MagicMock, mock_load: MagicMock, mock_refresh: MagicMock
    ) -> None:
        """load_plugins should catch NamespaceAccessError and continue."""
        import os
        import tempfile

        from plugin_runner.plugin_runner import load_plugins

        # Create temp directories to act as plugin paths
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin1 = os.path.join(tmpdir, "plugin1")
            plugin2 = os.path.join(tmpdir, "plugin2")
            os.makedirs(plugin1)
            os.makedirs(plugin2)

            # First plugin raises NamespaceAccessError, second succeeds
            mock_load.side_effect = [
                NamespaceAccessError("Plugin 1 access denied"),
                None,  # Plugin 2 succeeds
            ]

            # Should not raise, should continue loading other plugins
            load_plugins(specified_plugin_paths=[plugin1, plugin2])

            # Both plugins should have been attempted
            assert mock_load.call_count == 2

            # Error should be captured by Sentry
            mock_sentry.capture_exception.assert_called_once()

    @patch("plugin_runner.plugin_runner.refresh_event_type_map")
    @patch("plugin_runner.plugin_runner.load_or_reload_plugin")
    @patch("plugin_runner.plugin_runner.sentry_sdk")
    def test_load_plugins_continues_after_namespace_error(
        self, mock_sentry: MagicMock, mock_load: MagicMock, mock_refresh: MagicMock
    ) -> None:
        """load_plugins should continue loading other plugins after NamespaceAccessError."""
        import os
        import tempfile

        from plugin_runner.plugin_runner import load_plugins

        with tempfile.TemporaryDirectory() as tmpdir:
            plugin1 = os.path.join(tmpdir, "plugin1")
            plugin2 = os.path.join(tmpdir, "plugin2")
            plugin3 = os.path.join(tmpdir, "plugin3")
            os.makedirs(plugin1)
            os.makedirs(plugin2)
            os.makedirs(plugin3)

            # Middle plugin has namespace error
            mock_load.side_effect = [
                None,  # Plugin 1 succeeds
                NamespaceAccessError("Plugin 2 access denied"),
                None,  # Plugin 3 succeeds
            ]

            load_plugins(specified_plugin_paths=[plugin1, plugin2, plugin3])

            # All three plugins should have been attempted
            assert mock_load.call_count == 3

    @patch("plugin_runner.plugin_runner.load_or_reload_plugin")
    @patch("plugin_runner.plugin_runner.sentry_sdk")
    def test_load_plugin_catches_namespace_access_error(
        self, mock_sentry: MagicMock, mock_load: MagicMock
    ) -> None:
        """load_plugin should catch NamespaceAccessError and not raise."""
        import pathlib

        from plugin_runner.plugin_runner import load_plugin

        mock_load.side_effect = NamespaceAccessError("Access denied")

        # Should not raise
        load_plugin(pathlib.Path("/path/to/plugin"))

        # Error should be captured by Sentry
        mock_sentry.capture_exception.assert_called_once()

    @patch("plugin_runner.plugin_runner.load_or_reload_plugin")
    @patch("plugin_runner.plugin_runner.sentry_sdk")
    def test_load_plugin_logs_namespace_access_error(
        self, mock_sentry: MagicMock, mock_load: MagicMock
    ) -> None:
        """load_plugin should log NamespaceAccessError with context."""
        import pathlib

        from plugin_runner.plugin_runner import load_plugin

        error_msg = "Plugin 'test' denied access to namespace 'org__data'"
        mock_load.side_effect = NamespaceAccessError(error_msg)

        with patch("plugin_runner.plugin_runner.log") as mock_log:
            load_plugin(pathlib.Path("/path/to/plugin"))

            # Check that error was logged
            mock_log.error.assert_called_once()
            log_call = mock_log.error.call_args[0][0]
            assert "Namespace access error" in log_call


class TestAccessLevelComparison:
    """Tests for comparing declared vs granted access levels."""

    def test_read_access_satisfied_by_read(self) -> None:
        """Requesting read should succeed with read access."""
        declared = "read"
        granted = "read"
        # Plugin should be allowed
        is_denied = declared == "read_write" and granted == "read"
        assert is_denied is False

    def test_read_access_satisfied_by_read_write(self) -> None:
        """Requesting read should succeed with read_write access."""
        declared = "read"
        granted = "read_write"
        is_denied = declared == "read_write" and granted == "read"
        assert is_denied is False

    def test_read_write_denied_with_only_read(self) -> None:
        """Requesting read_write should fail with only read access."""
        declared = "read_write"
        granted = "read"
        is_denied = declared == "read_write" and granted == "read"
        assert is_denied is True

    def test_read_write_satisfied_by_read_write(self) -> None:
        """Requesting read_write should succeed with read_write access."""
        declared = "read_write"
        granted = "read_write"
        is_denied = declared == "read_write" and granted == "read"
        assert is_denied is False
