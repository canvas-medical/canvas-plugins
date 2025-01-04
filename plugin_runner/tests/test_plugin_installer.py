import json
import tarfile
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import MagicMock

from pytest_mock import MockerFixture

import settings
from plugin_runner.plugin_installer import download_plugin, install_plugins, uninstall_plugin


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


def _create_zip_archive(name: str) -> Path:
    # Create a temporary zip file
    temp_dir = tempfile.mkdtemp()
    zip_path = Path(f"{temp_dir}/{name}.zip")

    # Add some files to the zip archive
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for i in range(3):
            file_path = Path(temp_dir) / f"file{i}.txt"
            file_path.write_text(f"Content of file {i}")
            zipf.write(file_path, arcname=f"file{i}.txt")

    # Return a Path handle to the zip archive
    return zip_path


def test_plugin_installation_from_tarball(mocker: MockerFixture) -> None:
    """Test that plugins can be installed from tarballs."""
    mock_plugins = {
        "plugin1": {
            "version": "1.0",
            "package": "plugins/plugin1.tar.gz",
            "secrets": {"key1": "value1"},
        },
        "plugin2": {
            "version": "2.0",
            "package": "plugins/plugin2.tar.gz",
            "secrets": {"key2": "value2"},
        },
    }

    tarball_1 = _create_tarball("plugin1")
    tarball_2 = _create_tarball("plugin2")

    mocker.patch("plugin_runner.plugin_installer.enabled_plugins", return_value=mock_plugins)
    mocker.patch(
        "plugin_runner.plugin_installer.download_plugin", side_effect=[tarball_1, tarball_2]
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


def test_plugin_installation_from_zip_archive(mocker: MockerFixture) -> None:
    """Test that plugins can be installed from zip archives."""
    mock_plugins = {
        "plugin1": {
            "version": "1.0",
            "package": "plugins/plugin1.zip",
            "secrets": {"key1": "value1"},
        },
        "plugin2": {
            "version": "2.0",
            "package": "plugins/plugin2.zip",
            "secrets": {"key2": "value2"},
        },
    }

    zip_1 = _create_zip_archive("plugin1")
    zip_2 = _create_zip_archive("plugin2")

    mocker.patch("plugin_runner.plugin_installer.enabled_plugins", return_value=mock_plugins)
    mocker.patch("plugin_runner.plugin_installer.download_plugin", side_effect=[zip_1, zip_2])

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


def test_download(mocker: MockerFixture):
    """Test that the plugin package can be written to disk, mocking out S3."""
    mock_s3_client = MagicMock()
    mocker.patch("boto3.client", return_value=mock_s3_client)

    plugin_package = "plugins/plugin1.tar.gz"
    result = download_plugin(plugin_package)

    mock_s3_client.download_fileobj.assert_called_once_with(
        "canvas-client-media", f"{settings.CUSTOMER_IDENTIFIER}/{plugin_package}", mocker.ANY
    )
    assert result.exists()
