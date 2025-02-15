import json
import tarfile
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from pytest_mock import MockerFixture

from plugin_runner.installation import (
    PluginAttributes,
    _extract_rows_to_dict,
    download_plugin,
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


def test_download(mocker: MockerFixture) -> None:
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
