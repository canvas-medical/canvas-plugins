import json
import os
import shutil
from collections.abc import Callable, Generator
from contextlib import chdir
from datetime import datetime
from pathlib import Path
from typing import Any, cast
from unittest.mock import MagicMock, patch
from urllib.parse import urlparse

import pytest
from django.core.exceptions import ImproperlyConfigured
from typer.testing import CliRunner

import settings
from canvas_cli.apps.auth.utils import CONFIG_PATH

from .main import app


@pytest.fixture(scope="session")
def plugin_name() -> str:
    """The plugin name to be used for the canvas cli test."""
    return f"cli{datetime.now().timestamp()}".replace(".", "")


@pytest.fixture(scope="session")
def create_or_update_config_auth_file_for_testing(plugin_name: str) -> Generator[None, None, None]:
    """Creates the necessary config file for auth before performing cli tests."""
    if not settings.INTEGRATION_TEST_URL:
        raise ImproperlyConfigured("INTEGRATION_TEST_URL is not set")

    host = cast(str, urlparse(settings.INTEGRATION_TEST_URL).hostname).replace(
        ".canvasmedical.com", ""
    )
    client_id = settings.INTEGRATION_TEST_CLIENT_ID
    client_secret = settings.INTEGRATION_TEST_CLIENT_SECRET

    path = CONFIG_PATH
    if not path.exists():
        if not path.parent.exists():
            path.parent.mkdir()
        path.touch()

    temp_path = path.parent / "temp_credentials.ini"

    # Read the original content
    with open(path) as original_file:
        original_content = original_file.read()

    # Write new content to the original file
    with open(path, "w") as original_file:
        original_file.writelines(
            [
                f"[{host}]\n",
                f"client_id={client_id}\n",
                f"client_secret={client_secret}\n",
            ]
        )

    # Append original content to the temp file
    with open(temp_path, "a") as temp_file:
        temp_file.write(original_content)

    yield

    with open(temp_path) as temp:
        original_content = temp.read()
        with open(path, "w") as f:
            f.write(original_content)
    os.remove(temp_path)


@pytest.fixture(autouse=True, scope="session")
def write_plugin(
    cli_runner: CliRunner,
    integration_tests_plugins_dir: Path,
    plugin_name: str,
) -> Generator[Any, Any, Any]:
    """Writes a plugin to the file system."""
    with chdir(integration_tests_plugins_dir):
        cli_runner.invoke(app, "init", input=plugin_name)

    handler_code = """
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler
from logger import log

class TestHandler(BaseHandler):
    RESPONDS_TO = [EventType.Name(EventType.ASSESS_COMMAND__CONDITION_SELECTED)]

    def compute(self):
        log.info("I was inserted from my plugin's handler.")
        return []
"""
    plugin_dir = integration_tests_plugins_dir / plugin_name
    handlers_dir = plugin_dir / plugin_name / "handlers"

    # Ensure the handlers directory exists (it should from the template)
    handlers_dir.mkdir(parents=True, exist_ok=True)

    with open(handlers_dir / "test_handler.py", "w") as handler:
        handler.write(handler_code)

    # Update the CANVAS_MANIFEST.json to include the test handler
    manifest_path = plugin_dir / plugin_name / "CANVAS_MANIFEST.json"
    with open(manifest_path, "r+") as manifest_file:
        manifest_json = json.load(manifest_file)
        manifest_json["components"]["handlers"].append(
            {
                "class": f"{plugin_name}.handlers.test_handler:TestHandler",
                "description": "A handler for testing",
            }
        )
        manifest_file.seek(0)
        json.dump(manifest_json, manifest_file, indent=4)
        manifest_file.truncate()

    yield

    if plugin_dir.exists():
        shutil.rmtree(plugin_dir)


def list_empty_plugins(plugin_name: str) -> tuple[str, int, list[str], list[str]]:
    """List all plugins."""
    return ("list", 0, [], [f"{plugin_name}"])


def install_new_plugin(plugin_name: str) -> tuple[str, int, list[str], list[str]]:
    """Install a new plugin."""
    return (
        f"install {plugin_name}",
        0,
        [
            f"Plugin {plugin_name} has a valid CANVAS_MANIFEST.json file",
            "Installing plugin:",
            "Posting",
            f"Plugin {plugin_name} uploaded! Check logs for more details.",
        ],
        [],
    )


def list_newly_installed_plugin(plugin_name: str) -> tuple[str, int, list[str], list[str]]:
    """List all plugins, including newly installed one."""
    return ("list", 0, [f"{plugin_name}@0.0.1	enabled"], [])


def list_plugin_no_secrets(plugin_name: str) -> tuple[str, int, list[str], list[str]]:
    """List the secrets of the plugin."""
    return (
        f"config list {plugin_name}",
        0,
        [
            "No secrets configured",
        ],
        [],
    )


def reinstall_plugin(plugin_name: str) -> tuple[str, int, list[str], list[str]]:
    """Make a change and reinstall the plugin."""
    handler_code = """
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler
from logger import log

class AssessHandler(BaseHandler):
    RESPONDS_TO = [EventType.Name(EventType.ASSESS_COMMAND__CONDITION_SELECTED)]
    NARRATIVE_STRING = "EDITED HANDLER: I was inserted from my plugin's handler."

    def compute(self):
        log.info(self.NARRATIVE_STRING)
        return []
"""

    with open(f"./{plugin_name}/handlers/event_handlers.py", "w") as handler_file:
        handler_file.write(handler_code)

    # Update the CANVAS_MANIFEST.json to point to the new handler
    manifest_path = f"./{plugin_name}/CANVAS_MANIFEST.json"
    with open(manifest_path, "r+") as manifest_file:
        manifest_json = json.load(manifest_file)
        # Update the first handler in the list to point to our new AssessHandler
        manifest_json["components"]["handlers"][0] = {
            "class": f"{plugin_name}.handlers.event_handlers:AssessHandler",
            "description": "An edited handler for testing",
        }
        manifest_file.seek(0)
        json.dump(manifest_json, manifest_file, indent=4)
        manifest_file.truncate()

    return (
        f"install {plugin_name}",
        0,
        [
            f"Plugin {plugin_name} has a valid CANVAS_MANIFEST.json file",
            "Installing plugin:",
            "Posting",
            f"Plugin {plugin_name} already exists, updating instead...",
            "New plugin version uploaded! Check logs for more details.",
        ],
        [],
    )


def reinstall_plugin_invalid_secrets(plugin_name: str) -> tuple[str, int, list[str], list[str]]:
    """Reinstall plugin with invalid secrets."""
    return (
        f"install {plugin_name} --secret key=value",
        1,
        [
            'Status code 400: ["Non-existent secret(s): key"]',
        ],
        [],
    )


def list_plugin_secrets(plugin_name: str) -> tuple[str, int, list[str], list[str]]:
    """List the secrets of the plugin."""
    return (
        f"config list {plugin_name}",
        0,
        [
            "['key']",
        ],
        [],
    )


def configure_plugin_secrets(plugin_name: str) -> tuple[str, int, list[str], list[str]]:
    """Configure the plugin secrets."""
    return (
        f"config set {plugin_name} key=value1",
        0,
        [
            f"Updating plugin {plugin_name} from http://localhost:8000 with secrets=key",
            "Plugin secrets successfully updated.",
        ],
        [],
    )


def reinstall_plugin_valid_secrets(plugin_name: str) -> tuple[str, int, list[str], list[str]]:
    """Reinstall plugin with valid secrets."""
    with open(f"./{plugin_name}/CANVAS_MANIFEST.json", "r+") as manifest_file:
        manifest_json = json.load(manifest_file)
        manifest_json["secrets"] = ["key"]
        manifest_file.seek(0)
        json.dump(manifest_json, manifest_file)
        manifest_file.truncate()

    return (
        f"install {plugin_name} --secret key=value",
        0,
        [
            f"Plugin {plugin_name} has a valid CANVAS_MANIFEST.json file",
            "Installing plugin:",
            "Posting",
            f"Plugin {plugin_name} already exists, updating instead...",
            "New plugin version uploaded! Check logs for more details.",
        ],
        [],
    )


def disable_plugin(plugin_name: str) -> tuple[str, int, list[str], list[str]]:
    """Disable plugin."""
    return (
        f"disable {plugin_name}",
        0,
        [f"Disabling {plugin_name} using ", f"Plugin {plugin_name} successfully disabled!"],
        [],
    )


def list_disabled_plugin(plugin_name: str) -> tuple[str, int, list[str], list[str]]:
    """List disabled plugin."""
    return ("list", 0, [f"{plugin_name}@0.0.1	disabled"], [])


def enable_plugin(plugin_name: str) -> tuple[str, int, list[str], list[str]]:
    """Enable the disabled plugin."""
    return (
        f"enable {plugin_name}",
        0,
        [
            f"Enabling {plugin_name} using ",
            f"Plugin {plugin_name} successfully enabled!",
        ],
        [],
    )


def uninstall_enabled_plugin(plugin_name: str) -> tuple[str, int, list[str], list[str]]:
    """Try to uninstall the enabled plugin."""
    return (
        f"uninstall {plugin_name}",
        1,
        [
            f"Uninstalling {plugin_name} using",
            'Status code 403: {"detail":"Cannot delete an enabled plugin."}',
        ],
        [],
    )


def uninstall_disabled_plugin(plugin_name: str) -> tuple[str, int, list[str], list[str]]:
    """Uninstall the plugin."""
    return (
        f"uninstall {plugin_name}",
        0,
        [
            f"Uninstalling {plugin_name} using",
            f"Plugin {plugin_name} successfully uninstalled!",
        ],
        [],
    )


@pytest.mark.integtest
@patch("canvas_cli.apps.auth.utils.get_token")
@patch("canvas_cli.apps.auth.utils.set_token")
@pytest.mark.parametrize(
    "step",
    [
        (list_empty_plugins),
        (install_new_plugin),
        (list_newly_installed_plugin),
        (list_plugin_no_secrets),
        (reinstall_plugin),
        (reinstall_plugin_invalid_secrets),
        (reinstall_plugin_valid_secrets),
        (list_plugin_secrets),
        (configure_plugin_secrets),
        (disable_plugin),
        (list_disabled_plugin),
        (enable_plugin),
        (uninstall_enabled_plugin),
        (disable_plugin),
        (uninstall_disabled_plugin),
        (list_empty_plugins),
    ],
)
def test_canvas_list_install_disable_enable_uninstall(
    mock_get_token: MagicMock,
    mock_set_token: MagicMock,
    integration_tests_plugins_dir: Path,
    plugin_name: str,
    create_or_update_config_auth_file_for_testing: None,
    step: Callable,
    cli_runner: CliRunner,
) -> None:
    """Tests that the Canvas CLI can list, install, reinstall, disable, enable, and uninstall a plugin."""
    mock_get_token.return_value = None
    mock_set_token.return_value = None

    with chdir(integration_tests_plugins_dir / plugin_name):
        (command, expected_exit_code, expected_outputs, expected_no_outputs) = step(plugin_name)
        result = cli_runner.invoke(app, command)

        assert result.exit_code == expected_exit_code
        for expected_output in expected_outputs:
            assert expected_output in result.stdout
        for expected_no_output in expected_no_outputs:
            assert expected_no_output not in result.stdout
