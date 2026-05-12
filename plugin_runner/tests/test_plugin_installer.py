import json
import logging
import tarfile
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pytest_mock import MockerFixture

from plugin_runner.exceptions import NamespaceWaitTimeout, PluginInstallationError
from plugin_runner.installation import (
    PluginAttributes,
    _extract_rows_to_dict,
    download_plugin,
    enabled_plugins,
    install_plugin,
    install_plugins,
    uninstall_plugin,
)


def _create_tarball(name: str) -> Path:
    # Create a temporary tarball file
    temp_dir = tempfile.mkdtemp()
    tarball_path = Path(temp_dir) / f"{name}.tar.gz"

    # Add some files to the tarball
    with tarfile.open(tarball_path, "w:gz") as tar:
        for i in range(3):
            file_path = Path(temp_dir) / f"file{i}.txt"
            file_path.write_text(f"Content of file {i}")
            tar.add(file_path, arcname=f"file{i}.txt")

    # Return a Path handle to the tarball
    return tarball_path


def test_extract_rows_to_dict() -> None:
    """Test that database rows can be extracted to a dictionary with secrets appropriately attributed to plugin."""
    rows = [
        {
            "name": "plugin1",
            "version": "1.0",
            "package": "package1",
            "key": "key1",
            "value": "value1",
        },
        {
            "name": "plugin1",
            "version": "1.0",
            "package": "package1",
            "key": "key2",
            "value": "value2",
        },
        {"name": "plugin2", "version": "2.0", "package": "package2", "key": None, "value": None},
    ]

    expected_output = {
        "plugin1": {
            "version": "1.0",
            "package": "package1",
            "secrets": {"key1": "value1", "key2": "value2"},
        },
        "plugin2": {
            "version": "2.0",
            "package": "package2",
            "secrets": {},
        },
    }

    result = _extract_rows_to_dict(rows)
    assert result == expected_output


def test_enabled_plugins_orders_by_name(mocker: MockerFixture) -> None:
    """All containers must iterate plugins in the same order to avoid widening the install race."""
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = []
    mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
    mock_cursor.__exit__ = MagicMock(return_value=None)

    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=None)

    mocker.patch("plugin_runner.installation.open_database_connection", return_value=mock_conn)

    enabled_plugins()

    executed_sql = mock_cursor.execute.call_args[0][0]
    assert "ORDER BY name" in executed_sql


def test_plugin_installation_from_tarball(mocker: MockerFixture) -> None:
    """Test that plugins can be installed from tarballs."""
    mock_plugins = {
        "plugin1": PluginAttributes(
            version="1.0", package="plugins/plugin1.tar.gz", secrets={"key1": "value1"}
        ),
        "plugin2": PluginAttributes(
            version="1.0", package="plugins/plugin2.tar", secrets={"key2": "value2"}
        ),
    }

    tarball_1 = _create_tarball("plugin1")
    tarball_2 = _create_tarball("plugin2")

    mocker.patch("plugin_runner.installation.enabled_plugins", return_value=mock_plugins)

    def mock_download_plugin(package: str) -> MagicMock:
        mock_context = mocker.Mock()
        if package == "plugins/plugin1.tar.gz":
            mock_context.__enter__ = mocker.Mock(return_value=tarball_1)
        elif package == "plugins/plugin2.tar":
            mock_context.__enter__ = mocker.Mock(return_value=tarball_2)
        mock_context.__exit__ = mocker.Mock(return_value=None)
        return mock_context

    mocker.patch(
        "plugin_runner.installation.download_plugin",
        side_effect=mock_download_plugin,
    )

    install_plugins()
    assert Path("plugin_runner/tests/data/plugins/plugin1").exists()
    assert Path("plugin_runner/tests/data/plugins/plugin1/SECRETS.json").exists()
    with open("plugin_runner/tests/data/plugins/plugin1/SECRETS.json") as f:
        assert json.load(f) == mock_plugins["plugin1"]["secrets"]
    assert Path("plugin_runner/tests/data/plugins/plugin2").exists()
    assert Path("plugin_runner/tests/data/plugins/plugin2/SECRETS.json").exists()
    with open("plugin_runner/tests/data/plugins/plugin2/SECRETS.json") as f:
        assert json.load(f) == mock_plugins["plugin2"]["secrets"]

    uninstall_plugin("plugin1")
    uninstall_plugin("plugin2")
    assert not Path("plugin_runner/tests/data/plugins/plugin1").exists()
    assert not Path("plugin_runner/tests/data/plugins/plugin2").exists()


def test_install_plugin_logs_success_with_version(
    mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    """Test that install_plugin emits a success log including the plugin version."""
    plugin_name = "plugin_success_log"
    plugin_version = "1.2.3"
    attributes = PluginAttributes(
        version=plugin_version,
        package=f"plugins/{plugin_name}.tar.gz",
        secrets={},
    )

    tarball = _create_tarball(plugin_name)

    def mock_download_plugin(package: str) -> MagicMock:
        mock_context = mocker.Mock()
        mock_context.__enter__ = mocker.Mock(return_value=tarball)
        mock_context.__exit__ = mocker.Mock(return_value=None)
        return mock_context

    mocker.patch(
        "plugin_runner.installation.download_plugin",
        side_effect=mock_download_plugin,
    )

    try:
        with caplog.at_level(logging.INFO):
            install_plugin(plugin_name, attributes)

        success_messages = [
            record.message
            for record in caplog.records
            if "Successfully installed plugin" in record.message
        ]
        assert len(success_messages) == 1, (
            f"Expected exactly one success log message, got: {success_messages}"
        )
        assert plugin_name in success_messages[0]
        assert plugin_version in success_messages[0]
    finally:
        uninstall_plugin(plugin_name)


def test_install_plugin_writes_secrets_on_namespace_wait_timeout(
    mocker: MockerFixture,
) -> None:
    """On NamespaceWaitTimeout, secrets must still be written so the plugin stays operable."""
    plugin_name = "racing_plugin"
    attributes = PluginAttributes(
        version="1.0", package=f"plugins/{plugin_name}.tar.gz", secrets={}
    )

    def fake_extract(plugin_file_path: Path, plugin_installation_path: Path) -> None:
        plugin_installation_path.mkdir(parents=True, exist_ok=True)
        (plugin_installation_path / "CANVAS_MANIFEST.json").write_text(
            json.dumps(
                {
                    "name": plugin_name,
                    "custom_data": {"namespace": "org__racing", "access": "read_write"},
                }
            )
        )

    mock_download = MagicMock()
    mock_download.__enter__ = MagicMock(return_value=Path("unused.tar.gz"))
    mock_download.__exit__ = MagicMock(return_value=None)
    mocker.patch("plugin_runner.installation.download_plugin", return_value=mock_download)
    mocker.patch("plugin_runner.installation.extract_plugin", side_effect=fake_extract)
    mocker.patch("plugin_runner.installation.clear_registered_models")
    mocker.patch("plugin_runner.installation.compute_models_hash", return_value="abc123")
    mocker.patch("plugin_runner.installation.is_schema_manager", return_value=False)
    mocker.patch(
        "plugin_runner.installation.wait_for_namespace",
        side_effect=NamespaceWaitTimeout("namespace 'org__racing' not ready"),
    )
    mocker.patch(
        "plugin_runner.installation.fetch_plugin_secrets",
        return_value={"api_key": "fresh_value"},
    )
    mock_install_secrets = mocker.patch("plugin_runner.installation.install_plugin_secrets")
    mock_log = mocker.patch("plugin_runner.installation.log")

    try:
        with pytest.raises(NamespaceWaitTimeout):
            install_plugin(plugin_name, attributes)

        mock_install_secrets.assert_called_once_with(
            plugin_name=plugin_name, secrets={"api_key": "fresh_value"}
        )
        mock_log.exception.assert_not_called()
    finally:
        uninstall_plugin(plugin_name)


def test_install_plugins_does_not_disable_on_namespace_wait_timeout(
    mocker: MockerFixture,
) -> None:
    """Bootstrap race: when wait_for_namespace times out, the plugin must stay enabled."""
    mock_plugins = {
        "racing_plugin": PluginAttributes(
            version="1.0", package="plugins/racing_plugin.tar.gz", secrets={}
        ),
    }
    mocker.patch("plugin_runner.installation.enabled_plugins", return_value=mock_plugins)
    mocker.patch(
        "plugin_runner.installation.install_plugin",
        side_effect=NamespaceWaitTimeout("schema manager not ready"),
    )
    mock_disable = mocker.patch("plugin_runner.installation.disable_plugin")

    install_plugins()

    mock_disable.assert_not_called()


def test_install_plugins_disables_on_other_install_errors(
    mocker: MockerFixture,
) -> None:
    """Non-transient install failures must still disable the plugin."""
    mock_plugins = {
        "broken_plugin": PluginAttributes(
            version="1.0", package="plugins/broken_plugin.tar.gz", secrets={}
        ),
    }
    mocker.patch("plugin_runner.installation.enabled_plugins", return_value=mock_plugins)
    mocker.patch(
        "plugin_runner.installation.install_plugin",
        side_effect=PluginInstallationError("manifest invalid"),
    )
    mock_disable = mocker.patch("plugin_runner.installation.disable_plugin")

    install_plugins()

    mock_disable.assert_called_once_with("broken_plugin")


def test_download() -> None:
    """Test that the plugin package can be written to disk, mocking out S3."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"some content in a file"
    with patch("requests.request", return_value=mock_response) as mock_request:
        plugin_package = "plugins/plugin1.tar.gz"
        with download_plugin(plugin_package) as plugin_path:
            assert plugin_path.exists()
            assert plugin_path.read_bytes() == b"some content in a file"
        mock_request.assert_called_once()
