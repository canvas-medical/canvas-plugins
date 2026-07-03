import base64
import json
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
    _find_unresolvable_handlers,
    _validate_plugin_loads,
    install,
    list_secrets,
    parse_secrets,
    update,
    validate_manifest,
    validate_package,
)
from .plugin import list as plugin_list


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
    (plugin_dir / "node_modules").mkdir()
    (plugin_dir / "node_modules" / "left-pad.js").write_text("module.exports = {}")

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
        # node_modules should be excluded by default
        assert not any("node_modules" in name for name in names)


@pytest.mark.parametrize(
    "ignore_lines, expected_present, expected_ignored",
    [
        # 1. Empty ignore file
        (
            [],
            ["CANVAS_MANIFEST.json", "handlers"],
            [".hidden-dir", ".hidden.file", "symlink", "__pycache__", "node_modules"],
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

    mock_print.assert_called_once_with("No variables configured.")


@patch("canvas_cli.apps.plugin.plugin.print")
@patch("requests.get")
@patch("canvas_cli.apps.plugin.plugin.get_or_request_api_token")
@patch("canvas_cli.apps.plugin.plugin.plugin_url")
def test_list_follows_pagination(
    mock_plugin_url: Mock, mock_get_token: Mock, mock_requests_get: Mock, mock_print: Mock
) -> None:
    """Test that list follows the paginated `next` link until every plugin is returned."""
    host = "https://example.canvasmedical.com"
    mock_plugin_url.return_value = f"{host}/plugin-io/plugins/"
    mock_get_token.return_value = "test-token"

    next_url = f"{host}/plugin-io/plugins/?limit=100&offset=100"
    page_one = Mock()
    page_one.status_code = requests.codes.ok
    page_one.json.return_value = {
        "count": 150,
        "next": next_url,
        "previous": None,
        "results": [{"name": "alpha", "version": "1.0", "is_enabled": True}],
    }
    page_two = Mock()
    page_two.status_code = requests.codes.ok
    page_two.json.return_value = {
        "count": 150,
        "next": None,
        "previous": f"{host}/plugin-io/plugins/?limit=100",
        "results": [{"name": "beta", "version": "2.0", "is_enabled": False}],
    }
    mock_requests_get.side_effect = [page_one, page_two]

    plugin_list(host=host)

    assert mock_requests_get.call_count == 2
    mock_requests_get.assert_any_call(next_url, headers={"Authorization": "Bearer test-token"})
    mock_print.assert_any_call("alpha@1.0\tenabled")
    mock_print.assert_any_call("beta@2.0\tdisabled")


@patch("canvas_cli.apps.plugin.plugin.print")
@patch("requests.get")
@patch("canvas_cli.apps.plugin.plugin.get_or_request_api_token")
@patch("canvas_cli.apps.plugin.plugin.plugin_url")
def test_list_no_plugins(
    mock_plugin_url: Mock, mock_get_token: Mock, mock_requests_get: Mock, mock_print: Mock
) -> None:
    """Test that list reports when no plugins are installed."""
    host = "https://example.canvasmedical.com"
    mock_plugin_url.return_value = f"{host}/plugin-io/plugins/"
    mock_get_token.return_value = "test-token"

    response = Mock()
    response.status_code = requests.codes.ok
    response.json.return_value = {"count": 0, "next": None, "previous": None, "results": []}
    mock_requests_get.return_value = response

    plugin_list(host=host)

    mock_print.assert_called_once_with(f"No plugins are currently installed on {host}")


@patch("builtins.print")
@patch("builtins.open", new_callable=mock_open, read_data=b"fake package data")
@patch("requests.post")
@patch("canvas_cli.apps.plugin.plugin.plugin_url")
@patch("canvas_cli.apps.plugin.plugin._build_package")
@patch("canvas_cli.apps.plugin.plugin._lint_plugin_static")
@patch("canvas_cli.apps.plugin.plugin._validate_plugin_loads")
@patch("canvas_cli.apps.plugin.plugin.validate_manifest")
@patch("canvas_cli.apps.plugin.plugin.get_or_request_api_token")
@patch("pathlib.Path.is_dir")
@patch("pathlib.Path.exists")
def test_install_success_no_secrets(
    mock_exists: Mock,
    mock_is_dir: Mock,
    mock_get_token: Mock,
    mock_validate: Mock,
    mock_validate_loads: Mock,
    mock_lint: Mock,
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

    install(plugin_name=plugin_path, secrets=[], variables=[], is_enabled=True, host=host)

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


@patch("canvas_cli.apps.plugin.plugin.requests.post")
@patch("canvas_cli.apps.plugin.plugin._build_package")
@patch("canvas_cli.apps.plugin.plugin.validate_manifest")
@patch("canvas_cli.apps.plugin.plugin.get_or_request_api_token")
def test_install_blocks_on_sandbox_violation(
    mock_get_token: Mock,
    mock_validate: Mock,
    mock_build: Mock,
    mock_post: Mock,
    tmp_path: Path,
) -> None:
    """`canvas install` runs the static sandbox lint and aborts before building
    or uploading when a plugin has a sandbox-rejected construct.
    """
    mock_get_token.return_value = "test-token"
    mock_validate.return_value = None

    plugin = tmp_path / "bad_plugin"
    (plugin / "handlers").mkdir(parents=True)
    (plugin / "CANVAS_MANIFEST.json").write_text('{"name": "bad_plugin"}')
    (plugin / "handlers" / "h.py").write_text("setattr(object(), 'x', 1)\n")

    with pytest.raises(typer.Exit):
        install(
            plugin_name=plugin,
            secrets=[],
            variables=[],
            is_enabled=True,
            host="https://example.canvasmedical.com",
        )

    mock_build.assert_not_called()
    mock_post.assert_not_called()


@patch("builtins.open", new_callable=mock_open, read_data=b"fake package data")
@patch("requests.post")
@patch("canvas_cli.apps.plugin.plugin.plugin_url")
@patch("canvas_cli.apps.plugin.plugin._build_package")
@patch("canvas_cli.apps.plugin.plugin._lint_plugin_static")
@patch("canvas_cli.apps.plugin.plugin._validate_plugin_loads")
@patch("canvas_cli.apps.plugin.plugin.validate_manifest")
@patch("canvas_cli.apps.plugin.plugin.get_or_request_api_token")
@patch("pathlib.Path.is_dir")
@patch("pathlib.Path.exists")
def test_install_success_with_secrets(
    mock_exists: Mock,
    mock_is_dir: Mock,
    mock_get_token: Mock,
    mock_validate: Mock,
    mock_validate_loads: Mock,
    mock_lint: Mock,
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

    install(plugin_name=plugin_path, secrets=secrets, variables=[], is_enabled=True, host=host)

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


@patch("builtins.open", new_callable=mock_open, read_data=b"fake package data")
@patch("requests.post")
@patch("canvas_cli.apps.plugin.plugin.plugin_url")
@patch("canvas_cli.apps.plugin.plugin._build_package")
@patch("canvas_cli.apps.plugin.plugin._lint_plugin_static")
@patch("canvas_cli.apps.plugin.plugin._validate_plugin_loads")
@patch("canvas_cli.apps.plugin.plugin.validate_manifest")
@patch("canvas_cli.apps.plugin.plugin.get_or_request_api_token")
@patch("pathlib.Path.is_dir")
@patch("pathlib.Path.exists")
def test_install_disabled(
    mock_exists: Mock,
    mock_is_dir: Mock,
    mock_get_token: Mock,
    mock_validate: Mock,
    mock_validate_loads: Mock,
    mock_lint: Mock,
    mock_build: Mock,
    mock_plugin_url: Mock,
    mock_post: Mock,
    mock_open_file: Mock,
) -> None:
    """Test installing a plugin in the disabled state."""
    mock_exists.return_value = True
    mock_is_dir.return_value = True
    mock_get_token.return_value = "test-token"
    mock_validate.return_value = None

    mock_build.return_value = Path("/tmp/built-plugin.zip")
    mock_plugin_url.return_value = "https://example.canvasmedical.com/api/plugins"

    mock_response = Mock()
    mock_response.status_code = requests.codes.created
    mock_post.return_value = mock_response

    install(
        plugin_name=Path("/fake/plugin"),
        secrets=[],
        variables=[],
        is_enabled=False,
        host="https://example.canvasmedical.com",
    )

    mock_post.assert_called_once_with(
        "https://example.canvasmedical.com/api/plugins",
        data=[("is_enabled", False)],
        files={"package": mock_open_file.return_value.__enter__.return_value},
        headers={"Authorization": "Bearer test-token"},
    )


@patch("canvas_cli.apps.plugin.plugin.update")
@patch("canvas_cli.apps.plugin.plugin._get_name_from_metadata")
@patch("builtins.print")
@patch("builtins.open", new_callable=mock_open, read_data=b"fake package data")
@patch("requests.post")
@patch("canvas_cli.apps.plugin.plugin.plugin_url")
@patch("canvas_cli.apps.plugin.plugin._build_package")
@patch("canvas_cli.apps.plugin.plugin._lint_plugin_static")
@patch("canvas_cli.apps.plugin.plugin._validate_plugin_loads")
@patch("canvas_cli.apps.plugin.plugin.validate_manifest")
@patch("canvas_cli.apps.plugin.plugin.get_or_request_api_token")
@patch("pathlib.Path.is_dir")
@patch("pathlib.Path.exists")
def test_install_conflict_calls_update(
    mock_exists: Mock,
    mock_is_dir: Mock,
    mock_get_token: Mock,
    mock_validate: Mock,
    mock_validate_loads: Mock,
    mock_lint: Mock,
    mock_build: Mock,
    mock_plugin_url: Mock,
    mock_post: Mock,
    mock_open_file: Mock,
    mock_print: Mock,
    mock_get_name: Mock,
    mock_update: Mock,
) -> None:
    """When the install endpoint returns 409, fall back to calling `update` with the package name."""
    mock_exists.return_value = True
    mock_is_dir.return_value = True
    mock_get_token.return_value = "test-token"
    mock_validate.return_value = None

    built_path = Path("/tmp/built-plugin.zip")
    mock_build.return_value = built_path
    mock_plugin_url.return_value = "https://example.canvasmedical.com/api/plugins"

    mock_response = Mock()
    mock_response.status_code = requests.codes.conflict
    mock_post.return_value = mock_response

    mock_get_name.return_value = "existing-plugin"

    host = "https://example.canvasmedical.com"
    secrets = ["API_KEY=secret123"]

    install(
        plugin_name=Path("/fake/plugin"),
        secrets=secrets,
        variables=[],
        is_enabled=True,
        host=host,
    )

    mock_get_name.assert_called_once_with(host, "test-token", built_path)
    mock_update.assert_called_once_with(
        "existing-plugin",
        built_path,
        is_enabled=True,
        secrets=secrets,
        host=host,
    )
    mock_print.assert_any_call("Plugin existing-plugin already exists, updating instead...")


@patch("canvas_cli.apps.plugin.plugin.update")
@patch("canvas_cli.apps.plugin.plugin._get_name_from_metadata")
@patch("builtins.print")
@patch("builtins.open", new_callable=mock_open, read_data=b"fake package data")
@patch("requests.post")
@patch("canvas_cli.apps.plugin.plugin.plugin_url")
@patch("canvas_cli.apps.plugin.plugin._build_package")
@patch("canvas_cli.apps.plugin.plugin._lint_plugin_static")
@patch("canvas_cli.apps.plugin.plugin._validate_plugin_loads")
@patch("canvas_cli.apps.plugin.plugin.validate_manifest")
@patch("canvas_cli.apps.plugin.plugin.get_or_request_api_token")
@patch("pathlib.Path.is_dir")
@patch("pathlib.Path.exists")
def test_install_error_status_exits(
    mock_exists: Mock,
    mock_is_dir: Mock,
    mock_get_token: Mock,
    mock_validate: Mock,
    mock_validate_loads: Mock,
    mock_lint: Mock,
    mock_build: Mock,
    mock_plugin_url: Mock,
    mock_post: Mock,
    mock_open_file: Mock,
    mock_print: Mock,
    mock_get_name: Mock,
    mock_update: Mock,
) -> None:
    """When the install endpoint returns an unexpected error status, print details and exit."""
    mock_exists.return_value = True
    mock_is_dir.return_value = True
    mock_get_token.return_value = "test-token"
    mock_validate.return_value = None

    mock_build.return_value = Path("/tmp/built-plugin.zip")
    mock_plugin_url.return_value = "https://example.canvasmedical.com/api/plugins"

    mock_response = Mock()
    mock_response.status_code = requests.codes.bad_request
    mock_response.text = "bad request body"
    mock_post.return_value = mock_response

    with pytest.raises(typer.Exit):
        install(
            plugin_name=Path("/fake/plugin"),
            secrets=[],
            variables=[],
            is_enabled=True,
            host="https://example.canvasmedical.com",
        )

    mock_get_name.assert_not_called()
    mock_update.assert_not_called()
    mock_print.assert_any_call(f"Status code {requests.codes.bad_request}: bad request body")


@patch("canvas_cli.apps.plugin.plugin.update")
@patch("canvas_cli.apps.plugin.plugin._get_name_from_metadata")
@patch("builtins.print")
@patch("builtins.open", new_callable=mock_open, read_data=b"fake package data")
@patch("requests.post")
@patch("canvas_cli.apps.plugin.plugin.plugin_url")
@patch("canvas_cli.apps.plugin.plugin._build_package")
@patch("canvas_cli.apps.plugin.plugin._lint_plugin_static")
@patch("canvas_cli.apps.plugin.plugin._validate_plugin_loads")
@patch("canvas_cli.apps.plugin.plugin.validate_manifest")
@patch("canvas_cli.apps.plugin.plugin.get_or_request_api_token")
@patch("pathlib.Path.is_dir")
@patch("pathlib.Path.exists")
def test_install_conflict_without_package_name_exits(
    mock_exists: Mock,
    mock_is_dir: Mock,
    mock_get_token: Mock,
    mock_validate: Mock,
    mock_validate_loads: Mock,
    mock_lint: Mock,
    mock_build: Mock,
    mock_plugin_url: Mock,
    mock_post: Mock,
    mock_open_file: Mock,
    mock_print: Mock,
    mock_get_name: Mock,
    mock_update: Mock,
) -> None:
    """When the install endpoint returns 409 but the package name can't be extracted, exit."""
    mock_exists.return_value = True
    mock_is_dir.return_value = True
    mock_get_token.return_value = "test-token"
    mock_validate.return_value = None

    mock_build.return_value = Path("/tmp/built-plugin.zip")
    mock_plugin_url.return_value = "https://example.canvasmedical.com/api/plugins"

    mock_response = Mock()
    mock_response.status_code = requests.codes.conflict
    mock_response.text = "conflict"
    mock_post.return_value = mock_response

    mock_get_name.return_value = None

    with pytest.raises(typer.Exit):
        install(
            plugin_name=Path("/fake/plugin"),
            secrets=[],
            variables=[],
            is_enabled=True,
            host="https://example.canvasmedical.com",
        )

    mock_update.assert_not_called()
    mock_print.assert_any_call(f"Status code {requests.codes.conflict}: conflict")


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

    # Create handlers directory with the referenced handler file, so the
    # handler resolves where the runner will look for it.
    handlers_dir = plugin_dir / "handlers"
    handlers_dir.mkdir()
    (handlers_dir / "__init__.py").touch()
    (handlers_dir / "my_handler.py").write_text("""
from canvas_sdk.handlers import BaseHandler
from canvas_sdk.effects import Effect

class MyHandler(BaseHandler):
    RESPONDS_TO = "test"

    def compute(self) -> list[Effect]:
        return []
""")

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


def test_find_unresolvable_handlers_all_resolve(tmp_path: Path) -> None:
    """All declared handlers resolve to files where the runner will look."""
    plugin_dir = tmp_path / "test_plugin"
    (plugin_dir / "routes").mkdir(parents=True)
    (plugin_dir / "routes" / "api.py").touch()
    (plugin_dir / "apps").mkdir()
    (plugin_dir / "apps" / "chart.py").touch()
    (plugin_dir / "protocols").mkdir()
    (plugin_dir / "protocols" / "hook.py").touch()

    manifest = {
        "name": "test_plugin",
        "components": {
            "protocols": [{"class": "test_plugin.protocols.hook:Hook"}],
            "applications": [{"class": "test_plugin.apps.chart:ChartApp"}],
            "handlers": [{"class": "test_plugin.routes.api:API"}],
        },
    }

    assert _find_unresolvable_handlers(plugin_dir, manifest) == []


def test_find_unresolvable_handlers_detects_misplaced_manifest(tmp_path: Path) -> None:
    """A manifest above the package directory (so the package is nested one
    level too deep) is flagged — this is the spruce failure mode.
    """
    project_root = tmp_path / "project"
    # Package nested under project_root/test_plugin/ while the manifest lives at
    # project_root/, so the handler file is one directory too deep.
    package = project_root / "test_plugin" / "routes"
    package.mkdir(parents=True)
    (package / "api.py").touch()

    manifest = {
        "name": "test_plugin",
        "components": {
            "handlers": [{"class": "test_plugin.routes.api:API"}],
        },
    }

    # validate_manifest is run against project_root (where CANVAS_MANIFEST.json
    # sits), so the runner would look for project_root/routes/api.py — missing.
    unresolvable = _find_unresolvable_handlers(project_root, manifest)

    assert len(unresolvable) == 1
    class_ref, expected = unresolvable[0]
    assert class_ref == "test_plugin.routes.api:API"
    assert expected == "routes/api.py"


def test_find_unresolvable_handlers_detects_wrong_package_name(tmp_path: Path) -> None:
    """A handler whose leading module segment isn't the manifest name can't be
    loaded by the runner and is flagged.
    """
    plugin_dir = tmp_path / "test_plugin"
    (plugin_dir / "routes").mkdir(parents=True)
    (plugin_dir / "routes" / "api.py").touch()

    manifest = {
        "name": "test_plugin",
        "components": {
            "handlers": [{"class": "other_package.routes.api:API"}],
        },
    }

    unresolvable = _find_unresolvable_handlers(plugin_dir, manifest)

    assert len(unresolvable) == 1
    assert unresolvable[0][0] == "other_package.routes.api:API"


def test_validate_manifest_misplaced_manifest_exits(tmp_path: Path) -> None:
    """validate_manifest fails when a handler won't resolve at runtime."""
    project_root = tmp_path / "test_plugin"
    # Doubled package nesting: handler file is one level too deep.
    package = project_root / "test_plugin" / "routes"
    package.mkdir(parents=True)
    (package / "api.py").touch()

    manifest = {
        "sdk_version": "0.1.4",
        "plugin_version": "0.0.1",
        "name": "test_plugin",
        "description": "Test plugin",
        "components": {
            "handlers": [{"class": "test_plugin.routes.api:API", "description": "x"}],
            "commands": [],
            "content": [],
            "effects": [],
            "views": [],
        },
        "tags": {},
        "references": [],
        "license": "",
        "diagram": False,
        "readme": "./README.md",
    }
    (project_root / "CANVAS_MANIFEST.json").write_text(__import__("json").dumps(manifest))

    with pytest.raises(typer.Exit):
        validate_manifest(project_root)


@patch("canvas_cli.apps.plugin.plugin.print")
@patch("requests.get")
@patch("canvas_cli.apps.plugin.plugin.get_or_request_api_token")
@patch("canvas_cli.apps.plugin.plugin.plugin_url")
def test_list_secrets_with_variables_field(
    mock_plugin_url: Mock,
    mock_get_token: Mock,
    mock_requests_get: Mock,
    mock_print: Mock,
) -> None:
    """list_secrets renders is_set/not-set uniformly and never displays values."""
    mock_plugin_url.return_value = "https://example.canvasmedical.com/api/plugins/p/metadata"
    mock_get_token.return_value = "test-token"

    mock_response = Mock()
    mock_response.status_code = requests.codes.ok
    mock_response.json.return_value = {
        "variables": [
            {"name": "API_KEY", "sensitive": True, "is_set": True},
            {"name": "MISSING_SECRET", "sensitive": True, "is_set": False},
            {"name": "REGION", "sensitive": False, "is_set": True},
            {"name": "EMPTY_VAR", "sensitive": False, "is_set": False},
        ]
    }
    mock_requests_get.return_value = mock_response

    list_secrets(plugin="p", host="https://example.canvasmedical.com")

    printed = [c.args[0] for c in mock_print.call_args_list]
    assert any("API_KEY = [set]  (sensitive)" in p for p in printed)
    assert any("MISSING_SECRET = [not set]  (sensitive)" in p for p in printed)
    assert any("REGION = [set]" in p and "(sensitive)" not in p for p in printed)
    assert any("EMPTY_VAR = [not set]" in p and "(sensitive)" not in p for p in printed)


@patch("builtins.open", new_callable=mock_open, read_data=b"fake package data")
@patch("requests.post")
@patch("canvas_cli.apps.plugin.plugin.plugin_url")
@patch("canvas_cli.apps.plugin.plugin._build_package")
@patch("canvas_cli.apps.plugin.plugin._lint_plugin_static")
@patch("canvas_cli.apps.plugin.plugin._validate_plugin_loads")
@patch("canvas_cli.apps.plugin.plugin.validate_manifest")
@patch("canvas_cli.apps.plugin.plugin.get_or_request_api_token")
@patch("pathlib.Path.is_dir")
@patch("pathlib.Path.exists")
def test_install_with_variables_flag(
    mock_exists: Mock,
    mock_is_dir: Mock,
    mock_get_token: Mock,
    mock_validate: Mock,
    mock_validate_loads: Mock,
    mock_lint: Mock,
    mock_build: Mock,
    mock_plugin_url: Mock,
    mock_post: Mock,
    mock_open_file: Mock,
) -> None:
    """Test that --variable values are sent alongside --secret values as base64 secret pairs."""
    mock_exists.return_value = True
    mock_is_dir.return_value = True
    mock_get_token.return_value = "test-token"
    mock_validate.return_value = None
    mock_build.return_value = Path("/tmp/built-plugin.zip")
    mock_plugin_url.return_value = "https://example.canvasmedical.com/api/plugins"

    mock_response = Mock()
    mock_response.status_code = requests.codes.created
    mock_post.return_value = mock_response

    install(
        plugin_name=Path("/fake/plugin"),
        secrets=["API_KEY=secret123"],
        variables=["REGION=us-west-2", "FEATURE_FLAG=on"],
        is_enabled=True,
        host="https://example.canvasmedical.com",
    )

    expected_data = [
        ("is_enabled", True),
        ("secret", base64.b64encode(b"API_KEY=secret123").decode()),
        ("secret", base64.b64encode(b"REGION=us-west-2").decode()),
        ("secret", base64.b64encode(b"FEATURE_FLAG=on").decode()),
    ]
    mock_post.assert_called_once_with(
        "https://example.canvasmedical.com/api/plugins",
        data=expected_data,
        files={"package": mock_open_file.return_value.__enter__.return_value},
        headers={"Authorization": "Bearer test-token"},
    )


@patch("canvas_cli.apps.plugin.plugin.update")
@patch("canvas_cli.apps.plugin.plugin._get_name_from_metadata")
@patch("builtins.open", new_callable=mock_open, read_data=b"fake package data")
@patch("requests.post")
@patch("canvas_cli.apps.plugin.plugin.plugin_url")
@patch("canvas_cli.apps.plugin.plugin._build_package")
@patch("canvas_cli.apps.plugin.plugin._lint_plugin_static")
@patch("canvas_cli.apps.plugin.plugin._validate_plugin_loads")
@patch("canvas_cli.apps.plugin.plugin.validate_manifest")
@patch("canvas_cli.apps.plugin.plugin.get_or_request_api_token")
@patch("pathlib.Path.is_dir")
@patch("pathlib.Path.exists")
def test_install_conflict_passes_variables_to_update(
    mock_exists: Mock,
    mock_is_dir: Mock,
    mock_get_token: Mock,
    mock_validate: Mock,
    mock_validate_loads: Mock,
    mock_lint: Mock,
    mock_build: Mock,
    mock_plugin_url: Mock,
    mock_post: Mock,
    mock_open_file: Mock,
    mock_get_name: Mock,
    mock_update: Mock,
) -> None:
    """On 409 conflict, update() must receive secrets + variables merged and is_enabled."""
    mock_exists.return_value = True
    mock_is_dir.return_value = True
    mock_get_token.return_value = "test-token"
    mock_validate.return_value = None
    built = Path("/tmp/built-plugin.zip")
    mock_build.return_value = built
    mock_plugin_url.return_value = "https://example.canvasmedical.com/api/plugins"

    mock_response = Mock()
    mock_response.status_code = requests.codes.conflict
    mock_post.return_value = mock_response
    mock_get_name.return_value = "my-plugin"

    install(
        plugin_name=Path("/fake/plugin"),
        secrets=["S=1"],
        variables=["V=2"],
        is_enabled=False,
        host="https://example.canvasmedical.com",
    )

    mock_update.assert_called_once_with(
        "my-plugin",
        built,
        is_enabled=False,
        secrets=["S=1", "V=2"],
        host="https://example.canvasmedical.com",
    )


_CLEAN_HANDLER = """
from canvas_sdk.handlers import BaseHandler


class Handler(BaseHandler):
    def compute(self):
        return []
"""

_FORBIDDEN_IMPORT_HANDLER = """
import subprocess

from canvas_sdk.handlers import BaseHandler


class Handler(BaseHandler):
    def compute(self):
        return []
"""


def _scaffold_plugin(plugin_dir: Path, handler_body: str) -> Path:
    """Write a minimal, schema-valid plugin whose single handler module contains
    ``handler_body``. Returns the plugin directory.
    """
    name = plugin_dir.name
    (plugin_dir / "handlers").mkdir(parents=True)
    (plugin_dir / "__init__.py").touch()
    (plugin_dir / "handlers" / "__init__.py").touch()
    (plugin_dir / "README.md").write_text("readme")
    (plugin_dir / "handlers" / "my_handler.py").write_text(handler_body)

    manifest = {
        "sdk_version": "0.1.4",
        "plugin_version": "0.0.1",
        "name": name,
        "description": "test",
        "components": {
            "protocols": [
                {
                    "class": f"{name}.handlers.my_handler:Handler",
                    "description": "a handler",
                }
            ]
        },
        "tags": {},
        "references": [],
        "license": "",
        "diagram": False,
        "readme": "./README.md",
    }
    (plugin_dir / "CANVAS_MANIFEST.json").write_text(json.dumps(manifest))
    return plugin_dir


def test_validate_plugin_loads_success(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """A plugin whose handlers import cleanly under the sandbox passes."""
    plugin = _scaffold_plugin(tmp_path / "clean_loads_plugin", _CLEAN_HANDLER)

    _validate_plugin_loads(plugin)

    captured = capsys.readouterr()
    assert "✓ clean_loads_plugin.handlers.my_handler:Handler" in captured.out
    assert "load cleanly" in captured.out


def test_validate_plugin_loads_surfaces_sandbox_violation(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    """A disallowed import surfaces as a failure and exits non-zero."""
    plugin = _scaffold_plugin(tmp_path / "bad_loads_plugin", _FORBIDDEN_IMPORT_HANDLER)

    with pytest.raises(typer.Exit) as exc_info:
        _validate_plugin_loads(plugin)

    assert exc_info.value.exit_code == 1
    captured = capsys.readouterr()
    assert "✗ bad_loads_plugin.handlers.my_handler:Handler" in captured.out
    assert "'subprocess' is not an allowed import" in captured.out


def test_validate_command_passes_for_clean_plugin(tmp_path: Path, cli_runner: CliRunner) -> None:
    """`canvas validate` exits 0 when manifest and sandbox-load both succeed."""
    plugin = _scaffold_plugin(tmp_path / "clean_cmd_plugin", _CLEAN_HANDLER)

    result = cli_runner.invoke(app, ["validate", str(plugin)])

    assert result.exit_code == 0


def test_validate_command_fails_for_sandbox_violation(
    tmp_path: Path, cli_runner: CliRunner
) -> None:
    """`canvas validate` exits 1 when a handler fails to load in the sandbox."""
    plugin = _scaffold_plugin(tmp_path / "bad_cmd_plugin", _FORBIDDEN_IMPORT_HANDLER)

    result = cli_runner.invoke(app, ["validate", str(plugin)])

    assert result.exit_code == 1


def test_validate_plugin_loads_resolves_intra_package_imports(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    """A handler that imports from a sibling module in its own package loads
    cleanly — validation must make the plugin's package importable (mirroring
    how the runner loads installed plugins from PLUGIN_DIRECTORY).
    """
    handler_body = """
from multimod_plugin.constants import GREETING

from canvas_sdk.handlers import BaseHandler


class Handler(BaseHandler):
    def compute(self):
        return [GREETING]
"""
    plugin = _scaffold_plugin(tmp_path / "multimod_plugin", handler_body)
    (plugin / "constants.py").write_text('GREETING = "hello"\n')

    _validate_plugin_loads(plugin)

    captured = capsys.readouterr()
    assert "✓ multimod_plugin.handlers.my_handler:Handler" in captured.out
    assert "load cleanly" in captured.out
