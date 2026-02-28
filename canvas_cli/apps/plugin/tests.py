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

from .plugin import (
    _build_package,
    _find_unreferenced_handlers,
    install,
    list_secrets,
    parse_secrets,
    update,
    validate_manifest,
    validate_package,
)


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
    (plugin_dir / "__pycache__").mkdir()
    (plugin_dir / "__pycache__" / "module.cpython-312.pyc").write_bytes(b"\x00")
    (plugin_dir / "handlers" / ".crush").mkdir()
    (plugin_dir / "handlers" / ".crush" / "cache.json").write_text("{}")

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

    # handlers dir exists
    handlers = plugin / "handlers"
    assert handlers.exists()
    assert handlers.is_dir()

    # handler file exists in handlers dir
    handler = plugin / "handlers" / "event_handlers.py"
    assert handler.exists()
    assert handler.is_file()


def test_build_package(init_plugin: Path) -> None:
    """Tests that the package is built correctly."""
    package = _build_package(init_plugin)
    assert package.exists()
    assert package.is_file()
    assert package.name.endswith(".tar.gz")

    # check that the package contains the plugin files
    with tarfile.open(package, "r:gz") as tar:
        names = tar.getnames()
        assert "CANVAS_MANIFEST.json" in names
        assert "handlers" in names
        assert "README.md" in names
        # __pycache__ should be excluded by default
        assert not any("__pycache__" in name for name in names)
        # hidden directories nested inside subdirectories should be excluded
        assert not any(".crush" in name for name in names)


@pytest.mark.parametrize(
    "ignore_lines, expected_present, expected_ignored",
    [
        # 1. Empty ignore file
        (
            [],
            ["CANVAS_MANIFEST.json", "handlers"],
            [".hidden-dir", ".hidden.file", "symlink", "__pycache__"],
        ),
        # 2. Relative path
        (["*.md"], ["CANVAS_MANIFEST.json", "handlers"], ["README.md"]),
        # 3. Negated path
        (["*.md", "!*.json"], ["CANVAS_MANIFEST.json", "handlers"], ["README.md"]),
        # 4. Commented lines and mixed rules
        (
            ["*.md", "# this is a comment", "*.tmp"],
            ["CANVAS_MANIFEST.json", "handlers"],
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


# Tests for validate_manifest and _find_unreferenced_handlers


@pytest.fixture
def plugin_with_manifest(tmp_path: Path) -> Path:
    """Create a temporary plugin directory with a valid manifest."""
    plugin_dir = tmp_path / "test_plugin"
    plugin_dir.mkdir()

    manifest = {
        "sdk_version": "0.1.4",
        "plugin_version": "0.0.1",
        "name": "test_plugin",
        "description": "Test plugin",
        "components": {
            "handlers": [
                {
                    "class": "test_plugin.handlers.my_handler:MyHandler",
                    "description": "A test handler",
                }
            ],
            "commands": [],
            "content": [],
            "effects": [],
            "views": [],
        },
        "secrets": [],
        "tags": {},
        "references": [],
        "license": "",
        "diagram": False,
        "readme": "./README.md",
    }

    manifest_file = plugin_dir / "CANVAS_MANIFEST.json"
    manifest_file.write_text(__import__("json").dumps(manifest))

    # Create handlers directory
    handlers_dir = plugin_dir / "handlers"
    handlers_dir.mkdir()
    (handlers_dir / "__init__.py").touch()

    return plugin_dir


@pytest.fixture
def plugin_with_unreferenced_handler(tmp_path: Path) -> Path:
    """Create a plugin with an unreferenced handler."""
    plugin_dir = tmp_path / "test_plugin"
    plugin_dir.mkdir()

    manifest = {
        "sdk_version": "0.1.4",
        "plugin_version": "0.0.1",
        "name": "test_plugin",
        "description": "Test plugin",
        "components": {
            "handlers": [
                {
                    "class": "test_plugin.handlers.my_handler:MyHandler",
                    "description": "A test handler",
                }
            ],
            "commands": [],
            "content": [],
            "effects": [],
            "views": [],
        },
        "secrets": [],
        "tags": {},
        "references": [],
        "license": "",
        "diagram": False,
        "readme": "./README.md",
    }

    manifest_file = plugin_dir / "CANVAS_MANIFEST.json"
    manifest_file.write_text(__import__("json").dumps(manifest))

    # Create handlers directory with two handlers
    handlers_dir = plugin_dir / "handlers"
    handlers_dir.mkdir()
    (handlers_dir / "__init__.py").touch()

    # Referenced handler
    my_handler = handlers_dir / "my_handler.py"
    my_handler.write_text("""
from canvas_sdk.handlers import BaseHandler
from canvas_sdk.effects import Effect

class MyHandler(BaseHandler):
    RESPONDS_TO = "test"

    def compute(self) -> list[Effect]:
        return []
""")

    # Unreferenced handler
    another_handler = handlers_dir / "another_handler.py"
    another_handler.write_text("""
from canvas_sdk.handlers import BaseHandler
from canvas_sdk.effects import Effect

class UnreferencedHandler(BaseHandler):
    RESPONDS_TO = "test"

    def compute(self) -> list[Effect]:
        return []
""")

    return plugin_dir


def test_validate_manifest_success(
    plugin_with_manifest: Path, capsys: pytest.CaptureFixture
) -> None:
    """Test that validate_manifest succeeds with a valid manifest."""
    validate_manifest(plugin_with_manifest)

    captured = capsys.readouterr()
    assert f"Plugin {plugin_with_manifest} has a valid CANVAS_MANIFEST.json file" in captured.out


def test_validate_manifest_non_existent_directory() -> None:
    """Test that validate_manifest raises error for non-existent directory."""
    with pytest.raises(typer.BadParameter, match="does not exist"):
        validate_manifest(Path("/non/existent/path"))


def test_validate_manifest_not_a_directory(tmp_path: Path) -> None:
    """Test that validate_manifest raises error when path is not a directory."""
    file_path = tmp_path / "not_a_dir.txt"
    file_path.write_text("not a directory")

    with pytest.raises(typer.BadParameter, match="is not a directory"):
        validate_manifest(file_path)


def test_validate_manifest_missing_manifest_file(tmp_path: Path) -> None:
    """Test that validate_manifest raises error when CANVAS_MANIFEST.json is missing."""
    plugin_dir = tmp_path / "plugin"
    plugin_dir.mkdir()

    with pytest.raises(typer.BadParameter, match="does not have a CANVAS_MANIFEST.json file"):
        validate_manifest(plugin_dir)


def test_validate_manifest_invalid_json(tmp_path: Path) -> None:
    """Test that validate_manifest raises error for invalid JSON."""
    plugin_dir = tmp_path / "plugin"
    plugin_dir.mkdir()

    manifest_file = plugin_dir / "CANVAS_MANIFEST.json"
    manifest_file.write_text("{ invalid json }")

    with pytest.raises(typer.Abort):
        validate_manifest(plugin_dir)


@patch("canvas_cli.apps.plugin.plugin._find_unreferenced_handlers")
def test_validate_manifest_with_unreferenced_handlers(
    mock_find_unreferenced: Mock, plugin_with_manifest: Path, capsys: pytest.CaptureFixture
) -> None:
    """Test that validate_manifest warns about unreferenced handlers."""
    mock_find_unreferenced.return_value = ["test_plugin.handlers.unreferenced:UnreferencedHandler"]

    validate_manifest(plugin_with_manifest)

    captured = capsys.readouterr()
    assert "Warning: Found handler classes that are not referenced" in captured.out
    assert "test_plugin.handlers.unreferenced:UnreferencedHandler" in captured.out


def test_find_unreferenced_handlers_detects_unreferenced(
    plugin_with_unreferenced_handler: Path,
) -> None:
    """Test that _find_unreferenced_handlers correctly detects unreferenced handlers."""
    manifest = __import__("json").loads(
        (plugin_with_unreferenced_handler / "CANVAS_MANIFEST.json").read_text()
    )

    unreferenced = _find_unreferenced_handlers(plugin_with_unreferenced_handler, manifest)

    assert len(unreferenced) == 1
    assert "test_plugin.handlers.another_handler:UnreferencedHandler" in unreferenced


def test_find_unreferenced_handlers_all_referenced(tmp_path: Path) -> None:
    """Test that _find_unreferenced_handlers returns empty when all handlers are referenced."""
    plugin_dir = tmp_path / "test_plugin"
    plugin_dir.mkdir()

    manifest = {
        "components": {
            "handlers": [
                {
                    "class": "test_plugin.handlers.my_handler:MyHandler",
                    "description": "A test handler",
                }
            ]
        }
    }

    # Create handler
    handlers_dir = plugin_dir / "handlers"
    handlers_dir.mkdir()
    (handlers_dir / "__init__.py").touch()

    my_handler = handlers_dir / "my_handler.py"
    my_handler.write_text("""
from canvas_sdk.handlers import BaseHandler
from canvas_sdk.effects import Effect

class MyHandler(BaseHandler):
    RESPONDS_TO = "test"

    def compute(self) -> list[Effect]:
        return []
""")

    unreferenced = _find_unreferenced_handlers(plugin_dir, manifest)

    assert len(unreferenced) == 0


def test_find_unreferenced_handlers_protocols_key_backwards_compatibility(tmp_path: Path) -> None:
    """Test that _find_unreferenced_handlers works with 'protocols' key for backwards compatibility."""
    plugin_dir = tmp_path / "test_plugin"
    plugin_dir.mkdir()

    manifest = {
        "components": {
            "protocols": [
                {
                    "class": "test_plugin.protocols.my_protocol:MyProtocol",
                    "description": "A test protocol",
                }
            ]
        }
    }

    # Create protocol
    protocols_dir = plugin_dir / "protocols"
    protocols_dir.mkdir()
    (protocols_dir / "__init__.py").touch()

    my_protocol = protocols_dir / "my_protocol.py"
    my_protocol.write_text("""
from canvas_sdk.handlers import BaseHandler
from canvas_sdk.effects import Effect

class MyProtocol(BaseHandler):
    RESPONDS_TO = "test"

    def compute(self) -> list[Effect]:
        return []
""")

    unreferenced = _find_unreferenced_handlers(plugin_dir, manifest)

    assert len(unreferenced) == 0


def test_find_unreferenced_handlers_skips_test_files(tmp_path: Path) -> None:
    """Test that _find_unreferenced_handlers skips test files."""
    plugin_dir = tmp_path / "test_plugin"
    plugin_dir.mkdir()

    manifest: dict[str, Any] = {"components": {"handlers": []}}

    # Create handlers directory with test file
    handlers_dir = plugin_dir / "handlers"
    handlers_dir.mkdir()
    (handlers_dir / "__init__.py").touch()

    # Test file should be skipped
    test_file = handlers_dir / "test_handler.py"
    test_file.write_text("""
from canvas_sdk.handlers import BaseHandler
from canvas_sdk.effects import Effect

class TestHandler(BaseHandler):
    RESPONDS_TO = "test"

    def compute(self) -> list[Effect]:
        return []
""")

    # Tests directory should be skipped
    tests_dir = plugin_dir / "tests"
    tests_dir.mkdir()
    test_in_tests = tests_dir / "my_test.py"
    test_in_tests.write_text("""
from canvas_sdk.handlers import BaseHandler
from canvas_sdk.effects import Effect

class HandlerInTestDir(BaseHandler):
    RESPONDS_TO = "test"

    def compute(self) -> list[Effect]:
        return []
""")

    unreferenced = _find_unreferenced_handlers(plugin_dir, manifest)

    # Should not detect handlers in test files or test directories
    assert len(unreferenced) == 0


def test_find_unreferenced_handlers_skips_imported_classes(tmp_path: Path) -> None:
    """Test that _find_unreferenced_handlers skips imported classes."""
    plugin_dir = tmp_path / "test_plugin"
    plugin_dir.mkdir()

    manifest: dict[str, Any] = {"components": {"handlers": []}}

    # Create handler that imports BaseHandler
    handlers_dir = plugin_dir / "handlers"
    handlers_dir.mkdir()
    (handlers_dir / "__init__.py").touch()

    my_handler = handlers_dir / "my_handler.py"
    my_handler.write_text("""
from canvas_sdk.handlers import BaseHandler
from canvas_sdk.effects import Effect

# BaseHandler is imported, so should not be flagged as unreferenced
""")

    unreferenced = _find_unreferenced_handlers(plugin_dir, manifest)

    # Should not detect BaseHandler as it's imported, not defined in the module
    assert len(unreferenced) == 0


def test_find_unreferenced_handlers_handles_import_errors(tmp_path: Path) -> None:
    """Test that _find_unreferenced_handlers gracefully handles import errors."""
    plugin_dir = tmp_path / "test_plugin"
    plugin_dir.mkdir()

    manifest: dict[str, Any] = {"components": {"handlers": []}}

    # Create handler with import error
    handlers_dir = plugin_dir / "handlers"
    handlers_dir.mkdir()
    (handlers_dir / "__init__.py").touch()

    bad_handler = handlers_dir / "bad_handler.py"
    bad_handler.write_text("""
from non_existent_module import Something

class MyHandler:
    pass
""")

    # Should not raise error, just skip the file
    unreferenced = _find_unreferenced_handlers(plugin_dir, manifest)

    assert isinstance(unreferenced, list)


def test_find_unreferenced_handlers_mixed_handlers_and_protocols(tmp_path: Path) -> None:
    """Test detection when manifest has both 'handlers' and 'protocols' keys."""
    plugin_dir = tmp_path / "test_plugin"
    plugin_dir.mkdir()

    manifest = {
        "components": {
            "handlers": [
                {
                    "class": "test_plugin.handlers.handler1:Handler1",
                    "description": "Handler 1",
                }
            ],
            "protocols": [
                {
                    "class": "test_plugin.protocols.protocol1:Protocol1",
                    "description": "Protocol 1",
                }
            ],
        }
    }

    # Create handlers
    handlers_dir = plugin_dir / "handlers"
    handlers_dir.mkdir()
    (handlers_dir / "__init__.py").touch()

    handler1 = handlers_dir / "handler1.py"
    handler1.write_text("""
from canvas_sdk.handlers import BaseHandler
from canvas_sdk.effects import Effect

class Handler1(BaseHandler):
    RESPONDS_TO = "test"

    def compute(self) -> list[Effect]:
        return []
""")

    # Unreferenced handler
    handler2 = handlers_dir / "handler2.py"
    handler2.write_text("""
from canvas_sdk.handlers import BaseHandler
from canvas_sdk.effects import Effect

class Handler2(BaseHandler):
    RESPONDS_TO = "test"

    def compute(self) -> list[Effect]:
        return []
""")

    # Create protocols
    protocols_dir = plugin_dir / "protocols"
    protocols_dir.mkdir()
    (protocols_dir / "__init__.py").touch()

    protocol1 = protocols_dir / "protocol1.py"
    protocol1.write_text("""
from canvas_sdk.handlers import BaseHandler
from canvas_sdk.effects import Effect

class Protocol1(BaseHandler):
    RESPONDS_TO = "test"

    def compute(self) -> list[Effect]:
        return []
""")

    unreferenced = _find_unreferenced_handlers(plugin_dir, manifest)

    # Should only detect Handler2 as unreferenced
    assert len(unreferenced) == 1
    assert "test_plugin.handlers.handler2:Handler2" in unreferenced
