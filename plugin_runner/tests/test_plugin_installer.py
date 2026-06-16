import json
import logging
import tarfile
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests
from pytest_mock import MockerFixture

from plugin_runner import installation
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


def test_download_retries_on_transient_connection_error(mocker: MockerFixture) -> None:
    """A transient connection reset during download must be retried, not fatal (KOALA-4328).

    Before the fix a single ConnectionResetError (surfaced by requests as a
    ConnectionError) during a deploy/restart would propagate, get wrapped in
    PluginInstallationError, and disable the customer's plugin. The download
    should instead retry and recover when the next attempt succeeds.
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"recovered content"

    transient = requests.exceptions.ConnectionError(
        "('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))"
    )

    # Don't actually sleep between retries.
    mocker.patch("time.sleep")

    with patch(
        "requests.request",
        side_effect=[transient, mock_response],
    ) as mock_request:
        with download_plugin("plugins/plugin1.tar.gz") as plugin_path:
            assert plugin_path.exists()
            assert plugin_path.read_bytes() == b"recovered content"

        # First attempt reset the connection; the retry succeeded.
        assert mock_request.call_count == 2


def test_download_gives_up_after_exhausting_retries(mocker: MockerFixture) -> None:
    """When every download attempt resets, the error propagates after the configured retries.

    Exhausting retries is the only path that should still fail the install (and
    ultimately disable the plugin) — but only after we've genuinely tried.
    """
    transient = requests.exceptions.ConnectionError(
        "('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))"
    )

    mocker.patch("time.sleep")

    with (
        patch("requests.request", side_effect=transient) as mock_request,
        pytest.raises(requests.exceptions.ConnectionError),
        download_plugin("plugins/plugin1.tar.gz"),
    ):
        pass

    assert mock_request.call_count == installation.MAX_DOWNLOAD_ATTEMPTS


def test_download_retries_on_s3_5xx(mocker: MockerFixture) -> None:
    """An S3 5xx (e.g. "503 Service Unavailable"/SlowDown throttle) is transient (KOALA-4328).

    Observed in production: a deploy-time 503 from S3 surfaced via
    raise_for_status as an HTTPError and disabled the customer's plugin.
    """
    failing = MagicMock()
    failing.status_code = 503
    failing.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "503 Server Error: Service Unavailable", response=failing
    )

    ok = MagicMock()
    ok.status_code = 200
    ok.content = b"recovered content"
    ok.raise_for_status.return_value = None

    mocker.patch("time.sleep")

    with patch("requests.request", side_effect=[failing, ok]) as mock_request:
        with download_plugin("plugins/plugin1.tar.gz") as plugin_path:
            assert plugin_path.read_bytes() == b"recovered content"

        assert mock_request.call_count == 2


def test_download_does_not_retry_on_4xx(mocker: MockerFixture) -> None:
    """A 4xx (e.g. expired signature, missing object) is deterministic and must fail fast."""
    forbidden = MagicMock()
    forbidden.status_code = 403
    forbidden.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "403 Client Error: Forbidden", response=forbidden
    )

    mocker.patch("time.sleep")

    with (
        patch("requests.request", side_effect=[forbidden, forbidden]) as mock_request,
        pytest.raises(requests.exceptions.HTTPError),
        download_plugin("plugins/plugin1.tar.gz"),
    ):
        pass

    # No retry — we gave up after the first deterministic failure.
    assert mock_request.call_count == 1


def test_install_plugins_keeps_plugin_enabled_when_download_recovers(
    mocker: MockerFixture,
) -> None:
    """End-to-end (KOALA-4328): a transient download reset that recovers must not disable the plugin.

    This is the customer-facing guarantee — a connection reset during a deploy
    should never silently disable an otherwise-healthy plugin.
    """
    plugin_name = "resilient_plugin"
    mock_plugins = {
        plugin_name: PluginAttributes(
            version="1.0", package=f"plugins/{plugin_name}.tar.gz", secrets={}
        ),
    }
    tarball = _create_tarball(plugin_name)

    mocker.patch("plugin_runner.installation.enabled_plugins", return_value=mock_plugins)
    mocker.patch("time.sleep")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = tarball.read_bytes()

    transient = requests.exceptions.ConnectionError(
        "('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))"
    )

    mock_disable = mocker.patch("plugin_runner.installation.disable_plugin")

    try:
        with patch("requests.request", side_effect=[transient, mock_response]):
            install_plugins()

        mock_disable.assert_not_called()
    finally:
        uninstall_plugin(plugin_name)
