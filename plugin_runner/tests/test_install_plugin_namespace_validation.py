"""Tests for namespace handling during plugin installation.

The plugin runner automatically manages namespace access keys as system-owned
secrets. When a plugin declares custom_data, install_plugin delegates to
setup_read_write_namespace or verify_read_namespace_access depending on the
declared access level. Plugins without custom_data skip namespace setup entirely.
"""

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from plugin_runner.exceptions import PluginInstallationError
from plugin_runner.installation import install_plugin


def _fake_extract(manifest: dict[str, Any]) -> Callable[[Path, Path], None]:
    """Return a side_effect for extract_plugin that writes the manifest and a models/ dir."""

    def _extract(src: Path, dest: Path) -> None:
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "CANVAS_MANIFEST.json").write_text(json.dumps(manifest))
        # Create a models/ directory so compute_models_hash can run
        models_dir = dest / "models"
        models_dir.mkdir(exist_ok=True)
        (models_dir / "__init__.py").write_text("")

    return _extract


@patch("plugin_runner.installation.generate_plugin_migrations")
@patch("plugin_runner.installation.verify_read_namespace_access")
@patch("plugin_runner.installation.install_plugin_secrets")
@patch("plugin_runner.installation.extract_plugin")
@patch("plugin_runner.installation.download_plugin")
def test_read_access_delegates_to_verify(
    mock_download: MagicMock,
    mock_extract: MagicMock,
    mock_install_secrets: MagicMock,
    mock_verify_read: MagicMock,
    mock_gen_migrations: MagicMock,
    tmp_path: Path,
) -> None:
    """Plugin with read access should delegate to verify_read_namespace_access."""
    manifest = {
        "custom_data": {"namespace": "org__data", "access": "read"},
        "secrets": [],
    }

    mock_download.return_value.__enter__ = MagicMock(return_value=Path("/fake.tar.gz"))
    mock_download.return_value.__exit__ = MagicMock(return_value=False)
    mock_extract.side_effect = _fake_extract(manifest)

    with patch("plugin_runner.installation.PLUGIN_DIRECTORY", str(tmp_path)):
        install_plugin(
            "my_plugin",
            {"version": "1.0.0", "package": "pkg.tar.gz", "secrets": {}},
        )

    mock_verify_read.assert_called_once()


@patch("plugin_runner.installation.mark_namespace_ready")
@patch("plugin_runner.installation.compute_models_hash", return_value="fakehash123")
@patch("plugin_runner.installation.generate_plugin_migrations")
@patch("plugin_runner.installation.setup_read_write_namespace", return_value=True)
@patch("plugin_runner.installation.install_plugin_secrets")
@patch("plugin_runner.installation.extract_plugin")
@patch("plugin_runner.installation.download_plugin")
def test_read_write_access_delegates_to_setup(
    mock_download: MagicMock,
    mock_extract: MagicMock,
    mock_install_secrets: MagicMock,
    mock_setup_ns: MagicMock,
    mock_gen_migrations: MagicMock,
    mock_compute_hash: MagicMock,
    mock_mark_ready: MagicMock,
    tmp_path: Path,
) -> None:
    """Plugin with read_write access should delegate to setup and mark ready with hash."""
    manifest = {
        "custom_data": {"namespace": "org__data", "access": "read_write"},
        "secrets": [],
    }

    mock_download.return_value.__enter__ = MagicMock(return_value=Path("/fake.tar.gz"))
    mock_download.return_value.__exit__ = MagicMock(return_value=False)
    mock_extract.side_effect = _fake_extract(manifest)

    with patch("plugin_runner.installation.PLUGIN_DIRECTORY", str(tmp_path)):
        install_plugin(
            "my_plugin",
            {"version": "1.0.0", "package": "pkg.tar.gz", "secrets": {}},
        )

    mock_setup_ns.assert_called_once()
    mock_gen_migrations.assert_called_once()
    mock_mark_ready.assert_called_once_with("org__data", "my_plugin", "fakehash123")


@patch("plugin_runner.installation.verify_read_namespace_access")
@patch("plugin_runner.installation.setup_read_write_namespace")
@patch("plugin_runner.installation.install_plugin_secrets")
@patch("plugin_runner.installation.extract_plugin")
@patch("plugin_runner.installation.download_plugin")
def test_no_namespace_setup_without_custom_data(
    mock_download: MagicMock,
    mock_extract: MagicMock,
    mock_install_secrets: MagicMock,
    mock_setup_ns: MagicMock,
    mock_verify_read: MagicMock,
    tmp_path: Path,
) -> None:
    """Plugin without custom_data should skip namespace setup entirely."""
    manifest: dict[str, Any] = {"secrets": []}

    mock_download.return_value.__enter__ = MagicMock(return_value=Path("/fake.tar.gz"))
    mock_download.return_value.__exit__ = MagicMock(return_value=False)
    mock_extract.side_effect = _fake_extract(manifest)

    with patch("plugin_runner.installation.PLUGIN_DIRECTORY", str(tmp_path)):
        install_plugin(
            "my_plugin",
            {"version": "1.0.0", "package": "pkg.tar.gz", "secrets": {}},
        )

    mock_setup_ns.assert_not_called()
    mock_verify_read.assert_not_called()


# --- Non-schema-manager tests ---


@patch("plugin_runner.installation.is_schema_manager", return_value=False)
@patch("plugin_runner.installation.fetch_plugin_secrets", return_value={})
@patch("plugin_runner.installation.wait_for_namespace")
@patch("plugin_runner.installation.compute_models_hash", return_value="fakehash123")
@patch("plugin_runner.installation.install_plugin_secrets")
@patch("plugin_runner.installation.extract_plugin")
@patch("plugin_runner.installation.download_plugin")
def test_non_schema_manager_read_write_waits_for_namespace(
    mock_download: MagicMock,
    mock_extract: MagicMock,
    mock_install_secrets: MagicMock,
    mock_compute_hash: MagicMock,
    mock_wait: MagicMock,
    mock_fetch_secrets: MagicMock,
    mock_is_sm: MagicMock,
    tmp_path: Path,
) -> None:
    """Non-schema-manager with read_write access should wait for the schema manager."""
    manifest = {
        "custom_data": {"namespace": "org__data", "access": "read_write"},
        "secrets": [],
    }

    mock_download.return_value.__enter__ = MagicMock(return_value=Path("/fake.tar.gz"))
    mock_download.return_value.__exit__ = MagicMock(return_value=False)
    mock_extract.side_effect = _fake_extract(manifest)

    with patch("plugin_runner.installation.PLUGIN_DIRECTORY", str(tmp_path)):
        install_plugin(
            "my_plugin",
            {"version": "1.0.0", "package": "pkg.tar.gz", "secrets": {}},
        )

    mock_wait.assert_called_once_with("org__data", "my_plugin", "fakehash123")


@patch("plugin_runner.installation.is_schema_manager", return_value=False)
@patch("plugin_runner.installation.namespace_exists", return_value=True)
@patch("plugin_runner.installation.wait_for_namespace")
@patch("plugin_runner.installation.install_plugin_secrets")
@patch("plugin_runner.installation.extract_plugin")
@patch("plugin_runner.installation.download_plugin")
def test_non_schema_manager_read_only_proceeds_when_namespace_exists(
    mock_download: MagicMock,
    mock_extract: MagicMock,
    mock_install_secrets: MagicMock,
    mock_wait: MagicMock,
    mock_ns_exists: MagicMock,
    mock_is_sm: MagicMock,
    tmp_path: Path,
) -> None:
    """Non-schema-manager with read access should proceed immediately if namespace exists."""
    manifest = {
        "custom_data": {"namespace": "org__data", "access": "read"},
        "secrets": [],
    }

    mock_download.return_value.__enter__ = MagicMock(return_value=Path("/fake.tar.gz"))
    mock_download.return_value.__exit__ = MagicMock(return_value=False)
    mock_extract.side_effect = _fake_extract(manifest)

    with patch("plugin_runner.installation.PLUGIN_DIRECTORY", str(tmp_path)):
        install_plugin(
            "my_plugin",
            {"version": "1.0.0", "package": "pkg.tar.gz", "secrets": {}},
        )

    mock_ns_exists.assert_called_once_with("org__data")
    mock_wait.assert_not_called()


@patch("plugin_runner.installation.is_schema_manager", return_value=False)
@patch("plugin_runner.installation.namespace_exists", return_value=False)
@patch("plugin_runner.installation.install_plugin_secrets")
@patch("plugin_runner.installation.extract_plugin")
@patch("plugin_runner.installation.download_plugin")
def test_non_schema_manager_read_only_raises_when_namespace_missing(
    mock_download: MagicMock,
    mock_extract: MagicMock,
    mock_install_secrets: MagicMock,
    mock_ns_exists: MagicMock,
    mock_is_sm: MagicMock,
    tmp_path: Path,
) -> None:
    """Non-schema-manager with read access should raise if namespace doesn't exist."""
    manifest = {
        "custom_data": {"namespace": "org__data", "access": "read"},
        "secrets": [],
    }

    mock_download.return_value.__enter__ = MagicMock(return_value=Path("/fake.tar.gz"))
    mock_download.return_value.__exit__ = MagicMock(return_value=False)
    mock_extract.side_effect = _fake_extract(manifest)

    with (
        patch("plugin_runner.installation.PLUGIN_DIRECTORY", str(tmp_path)),
        pytest.raises(PluginInstallationError),
    ):
        install_plugin(
            "my_plugin",
            {"version": "1.0.0", "package": "pkg.tar.gz", "secrets": {}},
        )


@patch("plugin_runner.installation.is_schema_manager", return_value=False)
@patch("plugin_runner.installation.wait_for_namespace")
@patch("plugin_runner.installation.compute_models_hash", return_value="fakehash123")
@patch("plugin_runner.installation.extract_plugin")
@patch("plugin_runner.installation.download_plugin")
def test_non_schema_manager_secrets_file_contains_namespace_keys_after_install(
    mock_download: MagicMock,
    mock_extract: MagicMock,
    mock_compute_hash: MagicMock,
    mock_wait: MagicMock,
    mock_is_sm: MagicMock,
    tmp_path: Path,
) -> None:
    """KOALA-5378: a non-schema-manager's local SECRETS.json must contain the
    namespace access keys after install_plugin returns, even when
    attributes['secrets'] was snapshotted before the schema manager populated
    plugin_io_pluginsecret.

    The race: B's enabled_plugins() snapshot was taken at T (before keys
    existed), so attributes['secrets'] is empty. The schema manager finishes
    after T, committing namespace_read_write_access_key to the DB.
    wait_for_namespace then returns. B's local SECRETS.json must reflect the
    DB state at that point, not the stale snapshot.
    """
    plugin_name = "my_plugin"
    namespace = "org__data"
    rw_key = "fresh-uuid-from-schema-manager"
    manifest = {
        "custom_data": {"namespace": namespace, "access": "read_write"},
        "secrets": ["namespace_read_write_access_key"],
    }

    mock_download.return_value.__enter__ = MagicMock(return_value=Path("/fake.tar.gz"))
    mock_download.return_value.__exit__ = MagicMock(return_value=False)
    mock_extract.side_effect = _fake_extract(manifest)

    # By the time wait_for_namespace returns, the schema manager has committed
    # the namespace key to plugin_io_pluginsecret. Mock the DB cursor that a
    # post-fix refresh would query.
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        {"key": "namespace_read_write_access_key", "value": rw_key},
    ]
    mock_conn = MagicMock()
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

    with (
        patch("plugin_runner.installation.PLUGIN_DIRECTORY", str(tmp_path)),
        patch(
            "plugin_runner.installation.open_database_connection",
            return_value=mock_conn,
        ),
    ):
        install_plugin(
            plugin_name,
            {"version": "1.0.0", "package": "pkg.tar.gz", "secrets": {}},
        )

    secrets_path = tmp_path / plugin_name / "SECRETS.json"
    assert secrets_path.exists(), "install_plugin should have written SECRETS.json"
    on_disk = json.loads(secrets_path.read_text())
    assert on_disk.get("namespace_read_write_access_key") == rw_key, (
        f"SECRETS.json should contain the namespace key from the DB, got {on_disk!r}"
    )
