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

from plugin_runner.installation import install_plugin


def _fake_extract(manifest: dict[str, Any]) -> Callable[[Path, Path], None]:
    """Return a side_effect for extract_plugin that writes the manifest to the dest directory."""

    def _extract(src: Path, dest: Path) -> None:
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "CANVAS_MANIFEST.json").write_text(json.dumps(manifest))

    return _extract


@patch("plugin_runner.installation.generate_plugin_migrations")
@patch("plugin_runner.installation.initialize_namespace_partitions")
@patch("plugin_runner.installation.verify_read_namespace_access")
@patch("plugin_runner.installation.install_plugin_secrets")
@patch("plugin_runner.installation.extract_plugin")
@patch("plugin_runner.installation.download_plugin")
def test_read_access_delegates_to_verify(
    mock_download: MagicMock,
    mock_extract: MagicMock,
    mock_install_secrets: MagicMock,
    mock_verify_read: MagicMock,
    mock_init_partitions: MagicMock,
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


@patch("plugin_runner.installation.generate_plugin_migrations")
@patch("plugin_runner.installation.initialize_namespace_partitions")
@patch("plugin_runner.installation.setup_read_write_namespace", return_value=True)
@patch("plugin_runner.installation.install_plugin_secrets")
@patch("plugin_runner.installation.extract_plugin")
@patch("plugin_runner.installation.download_plugin")
def test_read_write_access_delegates_to_setup(
    mock_download: MagicMock,
    mock_extract: MagicMock,
    mock_install_secrets: MagicMock,
    mock_setup_ns: MagicMock,
    mock_init_partitions: MagicMock,
    mock_gen_migrations: MagicMock,
    tmp_path: Path,
) -> None:
    """Plugin with read_write access should delegate to setup_read_write_namespace."""
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
