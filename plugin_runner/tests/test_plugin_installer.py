import json
import logging
import tarfile
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import psycopg
import pytest
import requests
from pytest_mock import MockerFixture

from plugin_runner.exceptions import (
    NamespaceWaitTimeout,
    PluginInstallationError,
    TransientPluginInstallationError,
)
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


@pytest.mark.parametrize(
    "transient_exc",
    [
        pytest.param(
            requests.exceptions.ConnectionError("[Errno 104] Connection reset by peer"),
            id="connection-reset-during-s3-download",
        ),
        pytest.param(
            requests.exceptions.Timeout("Read timed out"),
            id="http-timeout-during-s3-download",
        ),
    ],
)
def test_install_plugins_does_not_disable_on_transient_download_failure(
    mocker: MockerFixture,
    transient_exc: Exception,
) -> None:
    """KOALA-5810: transient HTTP failures during S3 download must not auto-disable.

    Both vida (`vitals_visualizer` v0.35.1, urllib3 HTTP-retry traceback) and
    doctronic (`note_webhook_notification` v0.0.1, ConnectionResetError during
    S3 download) hit this path: `download_plugin` raised a transient transport
    error, `install_plugin` wrapped it to PluginInstallationError, and the
    `install_plugins` loop hard-disabled the plugin via raw SQL — leaving it
    disabled for ~32h (vida) and ~8 days (doctronic) until a human re-enabled.
    """
    mock_plugins = {
        "transient_plugin": PluginAttributes(
            version="1.0", package="plugins/transient_plugin.tar.gz", secrets={}
        ),
    }
    mocker.patch("plugin_runner.installation.enabled_plugins", return_value=mock_plugins)
    mock_download = mocker.patch(
        "plugin_runner.installation.download_plugin",
        side_effect=transient_exc,
    )
    mock_disable = mocker.patch("plugin_runner.installation.disable_plugin")
    mocker.patch("plugin_runner.installation.time.sleep")

    install_plugins()

    mock_disable.assert_not_called()
    # Retried up to the configured budget before giving up.
    assert mock_download.call_count == 3


def test_install_plugins_does_not_disable_on_transient_db_interface_error(
    mocker: MockerFixture,
) -> None:
    """KOALA-5810: transient psycopg InterfaceError must not auto-disable.

    Mirrors the vida (production) trigger: `InterfaceError('connection already
    closed')` surfaced from a DB op during install. `install_plugin`'s catch-all
    wraps it to PluginInstallationError and the loop disables the plugin. A
    transient DB connection blip should be retried, not turned into a sticky
    `is_enabled=False` that requires manual intervention.
    """
    plugin_name = "db_blip_plugin"
    mock_plugins = {
        plugin_name: PluginAttributes(
            version="1.0", package=f"plugins/{plugin_name}.tar.gz", secrets={}
        ),
    }

    def fake_extract(plugin_file_path: Path, plugin_installation_path: Path) -> None:
        plugin_installation_path.mkdir(parents=True, exist_ok=True)
        (plugin_installation_path / "CANVAS_MANIFEST.json").write_text(
            json.dumps(
                {
                    "name": plugin_name,
                    "custom_data": {"namespace": "org__blip", "access": "read_write"},
                }
            )
        )

    mock_download = MagicMock()
    mock_download.__enter__ = MagicMock(return_value=Path("unused.tar.gz"))
    mock_download.__exit__ = MagicMock(return_value=None)

    mocker.patch("plugin_runner.installation.enabled_plugins", return_value=mock_plugins)
    mocker.patch("plugin_runner.installation.download_plugin", return_value=mock_download)
    mocker.patch("plugin_runner.installation.extract_plugin", side_effect=fake_extract)
    mocker.patch("plugin_runner.installation.install_plugin_secrets")
    mocker.patch("plugin_runner.installation.clear_registered_models")
    mocker.patch("plugin_runner.installation.is_schema_manager", return_value=True)
    mock_setup = mocker.patch(
        "plugin_runner.installation.setup_read_write_namespace",
        side_effect=psycopg.InterfaceError("connection already closed"),
    )
    mock_disable = mocker.patch("plugin_runner.installation.disable_plugin")
    mocker.patch("plugin_runner.installation.time.sleep")

    try:
        install_plugins()
        mock_disable.assert_not_called()
        # Retried up to the configured budget before giving up.
        assert mock_setup.call_count == 3
    finally:
        uninstall_plugin(plugin_name)


def test_install_plugin_preserves_existing_files_on_transient_download_failure(
    mocker: MockerFixture,
) -> None:
    """KOALA-5810: a transient download failure must not destroy the working version.

    `install_plugin` defers the rmtree of the existing plugin directory until
    after the new package is on local disk. So when `download_plugin` raises
    `requests.ConnectionError`, the previously-loaded plugin remains intact
    and the worker keeps serving it until the next install pass retries.
    """
    from settings import PLUGIN_DIRECTORY

    plugin_name = "preserved_plugin"
    plugins_dir = Path(PLUGIN_DIRECTORY)
    plugins_dir.mkdir(parents=True, exist_ok=True)
    plugin_path = plugins_dir / plugin_name
    plugin_path.mkdir(parents=True, exist_ok=True)
    sentinel = plugin_path / "PLUGIN.py"
    sentinel.write_text("# old version still running")

    mocker.patch(
        "plugin_runner.installation.download_plugin",
        side_effect=requests.exceptions.ConnectionError("[Errno 104] Connection reset by peer"),
    )

    try:
        with pytest.raises(PluginInstallationError):
            install_plugin(
                plugin_name,
                PluginAttributes(
                    version="2.0", package=f"plugins/{plugin_name}.tar.gz", secrets={}
                ),
            )

        assert plugin_path.exists(), "old plugin directory must remain on disk"
        assert sentinel.read_text() == "# old version still running"
    finally:
        uninstall_plugin(plugin_name)


def test_install_plugins_retries_and_succeeds_after_transient_failure(
    mocker: MockerFixture,
) -> None:
    """A transient failure on attempt N should be retried and recover on attempt N+1."""
    mock_plugins = {
        "flaky_plugin": PluginAttributes(
            version="1.0", package="plugins/flaky_plugin.tar.gz", secrets={}
        ),
    }
    mocker.patch("plugin_runner.installation.enabled_plugins", return_value=mock_plugins)
    mock_install = mocker.patch(
        "plugin_runner.installation.install_plugin",
        side_effect=[
            TransientPluginInstallationError("connection reset"),
            None,
        ],
    )
    mock_disable = mocker.patch("plugin_runner.installation.disable_plugin")
    mocker.patch("plugin_runner.installation.time.sleep")

    install_plugins()

    assert mock_install.call_count == 2
    mock_disable.assert_not_called()


def test_install_plugins_disables_on_deterministic_install_error_without_retry(
    mocker: MockerFixture,
) -> None:
    """Deterministic failures (bad manifest, invalid format) still disable on first try.

    Regression guard: the new retry budget for transient errors must not extend
    to deterministic failures, which would waste time before the inevitable
    disable.
    """
    mock_plugins = {
        "broken_plugin": PluginAttributes(
            version="1.0", package="plugins/broken_plugin.tar.gz", secrets={}
        ),
    }
    mocker.patch("plugin_runner.installation.enabled_plugins", return_value=mock_plugins)
    mock_install = mocker.patch(
        "plugin_runner.installation.install_plugin",
        side_effect=PluginInstallationError("manifest invalid"),
    )
    mock_disable = mocker.patch("plugin_runner.installation.disable_plugin")
    mocker.patch("plugin_runner.installation.time.sleep")

    install_plugins()

    assert mock_install.call_count == 1
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
