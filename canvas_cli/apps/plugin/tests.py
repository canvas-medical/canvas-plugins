import base64
import shutil
import tarfile
from collections.abc import Generator
from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import Mock, mock_open, patch

import pytest
import requests
import typer
from typer.testing import CliRunner

from canvas_cli.main import app

from .plugin import _build_package, install, list_secrets, parse_secrets, update, validate_package


def test_validate_package_unexistant_path() -> None:
    """Tests the validate_package callback with an invalid folder."""
    with pytest.raises(typer.BadParameter):
        validate_package(Path("/a_random_url_that_will_not_exist_or_so_I_hope"))


def test_validate_package_wrong_file_type(tmp_path: Path) -> None:
    """Tests the validate_package callback with an invalid file type."""
    invalid_file = tmp_path / "tmp_file.zip"
    invalid_file.write_text("definitely not a python package")

    with pytest.raises(typer.BadParameter):
        validate_package(invalid_file)


def test_validate_package_valid_file(tmp_path: Path) -> None:
    """Tests the validate_package callback with a valid file type."""
    package_path = tmp_path / "test-package.whl"
    package_path.write_text("something")
    result = validate_package(package_path)
    assert result == package_path


@pytest.fixture
def init_plugin_name() -> str:
    """The plugin name to be used for the canvas cli init test."""
    return f"testing_init-{datetime.now().timestamp()}".replace(".", "")


@pytest.fixture(autouse=True)
def clean_up_plugin(init_plugin_name: str) -> Generator[Any, Any, Any]:
    """Cleans up the plugin directory after the test."""
    yield
    if Path(f"./{init_plugin_name}").exists():
        shutil.rmtree(Path(f"./{init_plugin_name}"))


@pytest.fixture
def init_plugin(cli_runner: CliRunner, init_plugin_name: str) -> Path:
    """Init the plugin and return the result."""
    cli_runner.invoke(app, "init", input=init_plugin_name)
    package_name = init_plugin_name.replace("-", "_")

    plugin_dir = Path(f"./{init_plugin_name}/{package_name}")

    (plugin_dir / ".hidden-dir").mkdir()
    (plugin_dir / ".hidden.file").touch()
    (plugin_dir / "symlink").symlink_to("target")

    return plugin_dir


def test_canvas_init(cli_runner: CliRunner, init_plugin_name: str) -> None:
    """Tests that the CLI successfully creates a plugin with init."""
    result = cli_runner.invoke(app, "init", input=init_plugin_name)
    package_name = init_plugin_name.replace("-", "_")
    assert result.exit_code == 0

    # plugin directory exists
    plugin = Path(f"./{init_plugin_name}/{package_name}")
    assert plugin.exists()
    assert plugin.is_dir()

    # manifest file exists
    manifest = plugin / "CANVAS_MANIFEST.json"
    assert manifest.exists()
    assert manifest.is_file()
    manifest_result = cli_runner.invoke(app, f"validate-manifest {plugin}")
    assert manifest_result.exit_code == 0

    # readme file exists
    readme = plugin / "README.md"
    assert readme.exists()
    assert readme.is_file()

    # protocols dir exists
    protocols = plugin / "protocols"
    assert protocols.exists()
    assert protocols.is_dir()

    # protocol file exists in protocols dir
    protocol = plugin / "protocols" / "my_protocol.py"
    assert protocol.exists()
    assert protocol.is_file()


def test_build_package(init_plugin: Path) -> None:
    """Tests that the package is built correctly."""
    package = _build_package(init_plugin)
    assert package.exists()
    assert package.is_file()
    assert package.name.endswith(".tar.gz")

    # check that the package contains the plugin files
    with tarfile.open(package, "r:gz") as tar:
        assert "CANVAS_MANIFEST.json" in tar.getnames()
        assert "protocols" in tar.getnames()
        assert "README.md" in tar.getnames()


@pytest.mark.parametrize(
    "ignore_lines, expected_present, expected_ignored",
    [
        # 1. Empty ignore file
        ([], ["CANVAS_MANIFEST.json", "protocols"], [".hidden-dir", ".hidden.file", "symlink"]),
        # 2. Relative path
        (["*.md"], ["CANVAS_MANIFEST.json", "protocols"], ["README.md"]),
        # 3. Negated path
        (["*.md", "!*.json"], ["CANVAS_MANIFEST.json", "protocols"], ["README.md"]),
        # 4. Commented lines and mixed rules
        (
            ["*.md", "# this is a comment", "*.tmp"],
            ["CANVAS_MANIFEST.json", "protocols"],
            ["README.md"],
        ),
    ],
    ids=[
        "default-ignored-patterns",
        "relative-path-ignore",
        "negated-path",
        "commented-rules",
    ],
)
def test_build_package_with_ignore_file(
    init_plugin: Path,
    ignore_lines: list[str],
    expected_present: list[str],
    expected_ignored: list[str],
) -> None:
    """Tests that the package is built correctly with ignore file."""
    with (
        patch.object(Path, "exists") as mock_exists,
        patch.object(Path, "read_text") as mock_read_text,
    ):
        mock_exists.return_value = True
        mock_read_text.return_value = "\n".join(ignore_lines)

        package = _build_package(init_plugin)
        assert package.exists()
        assert package.is_file()
        assert package.name.endswith(".tar.gz")

        with tarfile.open(package, "r:gz") as tar:
            names = set(tar.getnames())
            for name in expected_present:
                assert name in names, f"Expected {name} to be present"
            for name in expected_ignored:
                assert name not in names, f"Expected {name} to be ignored"


def test_parse_secrets_valid_single_secret() -> None:
    """Test parsing a single valid secret."""
    secrets = ["API_KEY=secret123"]
    result = parse_secrets(secrets)

    assert result == ["API_KEY=secret123"]
    assert len(result) == 1


def test_parse_secrets_valid_multiple_secrets() -> None:
    """Test parsing multiple valid secrets."""
    secrets = ["API_KEY=secret123", "DB_PASSWORD=mypassword", "TOKEN=abcdef123456"]
    result = parse_secrets(secrets)

    assert result == secrets
    assert len(result) == 3


def test_parse_secrets_empty_list() -> None:
    """Test parsing an empty list of secrets."""
    secrets: list[str] = []
    result = parse_secrets(secrets)

    assert result == []
    assert len(result) == 0


def test_parse_secrets_with_multiple_equals() -> None:
    """Test parsing secrets with multiple equals signs."""
    secrets = ["DATABASE_URL=postgres://user:pass=word@host:5432/db"]
    result = parse_secrets(secrets)

    assert result == ["DATABASE_URL=postgres://user:pass=word@host:5432/db"]


def test_parse_secrets_with_empty_value() -> None:
    """Test parsing secrets with empty values."""
    secrets = ["EMPTY_SECRET=", "ANOTHER_KEY="]
    result = parse_secrets(secrets)

    assert result == ["EMPTY_SECRET=", "ANOTHER_KEY="]


def test_parse_secrets_invalid_no_equals() -> None:
    """Test that secrets without equals sign raise BadParameter."""
    secrets = ["INVALID_SECRET"]

    with pytest.raises(
        typer.BadParameter, match="Invalid secret format: 'INVALID_SECRET'. Use key=value."
    ):
        parse_secrets(secrets)


@patch("canvas_cli.apps.plugin.plugin.print")
@patch("requests.get")
@patch("canvas_cli.apps.plugin.plugin.get_or_request_api_token")
@patch("canvas_cli.apps.plugin.plugin.plugin_url")
def test_list_secrets_success_with_secrets(
    mock_plugin_url: Mock, mock_get_token: Mock, mock_requests_get: Mock, mock_print: Mock
) -> None:
    """Test successful listing of secrets when secrets exist."""
    plugin = "test-plugin"
    host = "https://example.canvasmedical.com"
    mock_plugin_url.return_value = (
        "https://example.canvasmedical.com/api/plugins/test-plugin/metadata"
    )
    mock_get_token.return_value = "test-token"

    mock_response = Mock()
    mock_response.status_code = requests.codes.ok
    mock_response.json.return_value = {"secrets": ["API_KEY", "DB_PASSWORD", "SECRET_TOKEN"]}
    mock_requests_get.return_value = mock_response

    with patch("canvas_cli.apps.plugin.plugin.pprint") as mock_pprint:
        list_secrets(plugin=plugin, host=host)

        mock_plugin_url.assert_called_once_with(host, plugin, "metadata")
        mock_get_token.assert_called_once_with(host)
        mock_pprint.assert_called_once_with(["API_KEY", "DB_PASSWORD", "SECRET_TOKEN"])
        mock_print.assert_not_called()


@patch("canvas_cli.apps.plugin.plugin.print")
@patch("requests.get")
@patch("canvas_cli.apps.plugin.plugin.get_or_request_api_token")
@patch("canvas_cli.apps.plugin.plugin.plugin_url")
def test_list_secrets_success_no_secrets(
    mock_plugin_url: Mock, mock_get_token: Mock, mock_requests_get: Mock, mock_print: Mock
) -> None:
    """Test successful response but no secrets configured."""
    plugin = "empty-plugin"
    host = "https://example.canvasmedical.com"
    mock_plugin_url.return_value = (
        "https://example.canvasmedical.com/api/plugins/empty-plugin/metadata"
    )
    mock_get_token.return_value = "test-token"

    mock_response = Mock()
    mock_response.status_code = requests.codes.ok
    mock_response.json.return_value = {"secrets": []}
    mock_requests_get.return_value = mock_response

    list_secrets(plugin=plugin, host=host)

    mock_print.assert_called_once_with("No secrets configured.")


@patch("builtins.print")
@patch("builtins.open", new_callable=mock_open, read_data=b"fake package data")
@patch("requests.post")
@patch("canvas_cli.apps.plugin.plugin.plugin_url")
@patch("canvas_cli.apps.plugin.plugin._build_package")
@patch("canvas_cli.apps.plugin.plugin.validate_manifest")
@patch("canvas_cli.apps.plugin.plugin.get_or_request_api_token")
@patch("pathlib.Path.is_dir")
@patch("pathlib.Path.exists")
def test_install_success_no_secrets(
    mock_exists: Mock,
    mock_is_dir: Mock,
    mock_get_token: Mock,
    mock_validate: Mock,
    mock_build: Mock,
    mock_plugin_url: Mock,
    mock_post: Mock,
    mock_open_file: Mock,
    mock_print: Mock,
) -> None:
    """Test successful plugin installation without secrets."""
    mock_exists.return_value = True
    mock_is_dir.return_value = True
    mock_get_token.return_value = "test-token"
    mock_validate.return_value = None

    built_path = Path("/tmp/built-plugin.zip")
    mock_build.return_value = built_path
    mock_plugin_url.return_value = "https://example.canvasmedical.com/api/plugins"

    mock_response = Mock()
    mock_response.status_code = requests.codes.created
    mock_post.return_value = mock_response

    plugin_path = Path("/fake/plugin")
    host = "https://example.canvasmesdical.com"

    install(plugin_name=plugin_path, secrets=[], host=host)

    mock_validate.assert_called_once_with(plugin_path)
    mock_build.assert_called_once_with(plugin_path)
    mock_plugin_url.assert_called_once_with(host)

    expected_data = [("is_enabled", True)]
    mock_post.assert_called_once_with(
        "https://example.canvasmedical.com/api/plugins",
        data=expected_data,
        files={"package": mock_open_file.return_value.__enter__.return_value},
        headers={"Authorization": "Bearer test-token"},
    )

    mock_print.assert_any_call(f"Installing plugin: {built_path} into {host}")
    mock_print.assert_any_call(
        f"Posting {built_path.absolute()} to https://example.canvasmedical.com/api/plugins"
    )
    mock_print.assert_any_call(f"Plugin {plugin_path} uploaded! Check logs for more details.")


@patch("builtins.open", new_callable=mock_open, read_data=b"fake package data")
@patch("requests.post")
@patch("canvas_cli.apps.plugin.plugin.plugin_url")
@patch("canvas_cli.apps.plugin.plugin._build_package")
@patch("canvas_cli.apps.plugin.plugin.validate_manifest")
@patch("canvas_cli.apps.plugin.plugin.get_or_request_api_token")
@patch("pathlib.Path.is_dir")
@patch("pathlib.Path.exists")
def test_install_success_with_secrets(
    mock_exists: Mock,
    mock_is_dir: Mock,
    mock_get_token: Mock,
    mock_validate: Mock,
    mock_build: Mock,
    mock_plugin_url: Mock,
    mock_post: Mock,
    mock_open_file: Mock,
) -> None:
    """Test successful plugin installation with secrets."""
    mock_exists.return_value = True
    mock_is_dir.return_value = True
    mock_get_token.return_value = "test-token"
    mock_validate.return_value = None

    built_path: Path = Path("/tmp/built-plugin.zip")
    mock_build.return_value = built_path
    mock_plugin_url.return_value = "https://example.canvasmedical.com/api/plugins"

    mock_response = Mock()
    mock_response.status_code = requests.codes.created
    mock_post.return_value = mock_response

    plugin_path: Path = Path("/fake/plugin")
    host = "https://example.canvasmedical.com"
    secrets = ["API_KEY=secret123", "DB_PASSWORD=mypassword"]

    install(plugin_name=plugin_path, secrets=secrets, host=host)

    expected_encoded_secrets = [
        ("secret", base64.b64encode(b"API_KEY=secret123").decode()),
        ("secret", base64.b64encode(b"DB_PASSWORD=mypassword").decode()),
    ]
    expected_data = [("is_enabled", True)] + expected_encoded_secrets

    mock_post.assert_called_once_with(
        "https://example.canvasmedical.com/api/plugins",
        data=expected_data,
        files={"package": mock_open_file.return_value.__enter__.return_value},
        headers={"Authorization": "Bearer test-token"},
    )


@patch("builtins.print")
@patch("builtins.open", new_callable=mock_open, read_data=b"fake package data")
@patch("requests.patch")
@patch("canvas_cli.apps.plugin.plugin.plugin_url")
@patch("canvas_cli.apps.plugin.plugin.validate_package")
@patch("canvas_cli.apps.plugin.plugin.get_or_request_api_token")
def test_update_with_package(
    mock_get_token: Mock,
    mock_validate: Mock,
    mock_plugin_url: Mock,
    mock_patch: Mock,
    mock_open_file: Mock,
    mock_print: Mock,
) -> None:
    """Test updating plugin with a new package."""
    mock_get_token.return_value = "test-token"
    mock_validate.return_value = None
    mock_plugin_url.return_value = "https://example.canvasmedical.com/api/plugins/test-plugin"

    mock_response = Mock()
    mock_response.status_code = requests.codes.ok
    mock_patch.return_value = mock_response

    name = "test-plugin"
    host = "https://example.canvasmedical.com"
    package_path: Path = Path("/path/to/package.tar.gz")

    update(name=name, package_path=package_path, host=host, secrets=[], is_enabled=None)

    mock_validate.assert_called_once_with(package_path)

    mock_patch.assert_called_once_with(
        "https://example.canvasmedical.com/api/plugins/test-plugin",
        data=[],
        headers={"Authorization": "Bearer test-token"},
        files={"package": mock_open_file.return_value.__enter__.return_value},
    )

    mock_print.assert_any_call(
        "Updating plugin test-plugin from https://example.canvasmedical.com with package_path=/path/to/package.tar.gz"
    )
    mock_print.assert_any_call("New plugin version uploaded! Check logs for more details.")


@patch("builtins.print")
@patch("requests.patch")
@patch("canvas_cli.apps.plugin.plugin.plugin_url")
@patch("canvas_cli.apps.plugin.plugin.get_or_request_api_token")
def test_update_secrets_only(
    mock_get_token: Mock, mock_plugin_url: Mock, mock_patch: Mock, mock_print: Mock
) -> None:
    """Test updating plugin with secrets only."""
    mock_get_token.return_value = "test-token"
    mock_plugin_url.return_value = "https://example.canvasmedical.com/api/plugins/test-plugin"

    mock_response = Mock()
    mock_response.status_code = requests.codes.ok
    mock_patch.return_value = mock_response

    name = "test-plugin"
    host = "https://example.canvasmedical.com"
    secrets = ["API_KEY=secret123", "DB_PASSWORD=mypassword"]

    update(name=name, secrets=secrets, host=host, package_path=None, is_enabled=None)

    mock_get_token.assert_called_once_with(host)
    mock_plugin_url.assert_called_once_with(host, name)

    expected_encoded_secrets = [
        ("secret", base64.b64encode(b"API_KEY=secret123").decode()),
        ("secret", base64.b64encode(b"DB_PASSWORD=mypassword").decode()),
    ]

    mock_patch.assert_called_once_with(
        "https://example.canvasmedical.com/api/plugins/test-plugin",
        data=expected_encoded_secrets,
        headers={"Authorization": "Bearer test-token"},
    )

    mock_print.assert_any_call(
        "Updating plugin test-plugin from https://example.canvasmedical.com with secrets=API_KEY,DB_PASSWORD"
    )
    mock_print.assert_any_call("Plugin secrets successfully updated.")


@patch("builtins.print")
@patch("requests.patch")
@patch("canvas_cli.apps.plugin.plugin.plugin_url")
@patch("canvas_cli.apps.plugin.plugin.get_or_request_api_token")
def test_update_enable_disable_only(
    mock_get_token: Mock, mock_plugin_url: Mock, mock_patch: Mock, mock_print: Mock
) -> None:
    """Test updating plugin enable/disable status only."""
    mock_get_token.return_value = "test-token"
    mock_plugin_url.return_value = "https://example.canvasmedical.com/api/plugins/test-plugin"

    mock_response = Mock()
    mock_response.status_code = requests.codes.ok
    mock_patch.return_value = mock_response

    name = "test-plugin"
    host = "https://example.canvasmedical.com"
    is_enabled = True

    update(name=name, is_enabled=is_enabled, host=host, package_path=None, secrets=[])

    expected_data = [("is_enabled", True)]

    mock_patch.assert_called_once_with(
        "https://example.canvasmedical.com/api/plugins/test-plugin",
        data=expected_data,
        headers={"Authorization": "Bearer test-token"},
    )

    mock_print.assert_any_call(
        "Updating plugin test-plugin from https://example.canvasmedical.com with is_enabled=True"
    )
