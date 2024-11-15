import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Generator, cast
from unittest.mock import MagicMock, patch
from urllib.parse import urlparse

import pytest
from django.core.exceptions import ImproperlyConfigured
from typer.testing import CliRunner

import settings
from canvas_cli.apps.auth.utils import CONFIG_PATH

from .main import app

runner = CliRunner()


@pytest.fixture(scope="session")
def plugin_name() -> str:
    """The plugin name to be used for the canvas cli test"""
    return f"cli-{datetime.now().timestamp()}".replace(".", "")


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

    original_content = open(path, "r").read()
    open(path, "w").writelines(
        [
            f"[{host}]\n",
            f"client_id={client_id}\n",
            f"client_secret={client_secret}\n",
        ]
    )
    open(temp_path, "a").write(original_content)

    yield

    with open(temp_path, "r") as temp:
        original_content = temp.read()
        with open(path, "w") as f:
            f.write(original_content)
    os.remove(temp_path)


@pytest.fixture(autouse=True, scope="session")
def write_plugin(plugin_name: str) -> Generator[Any, Any, Any]:
    runner.invoke(app, "init", input=plugin_name)
    protocol = open(f"./{plugin_name}/protocols/my_protocol.py", "w")
    p = """
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from logger import log

class Protocol(BaseProtocol):
    RESPONDS_TO = EventType.Name(EventType.ASSESS_COMMAND__CONDITION_SELECTED)
    NARRATIVE_STRING = "I was inserted from my plugin's protocol."

    def compute(self):
        log.info(self.NARRATIVE_STRING)
        return []
"""
    protocol.write(p)
    protocol.close()

    yield

    if Path(f"./{plugin_name}").exists():
        shutil.rmtree(Path(f"./{plugin_name}"))


def list_empty_plugins(plugin_name: str) -> tuple[str, int, list[str], list[str]]:
    """Step 1 - list all plugins"""
    return ("list", 0, [], [f"{plugin_name}"])


def install_new_plugin(plugin_name: str) -> tuple[str, int, list[str], list[str]]:
    """Step 2 - install a new plugin"""
    return (
        f"install {plugin_name}",
        0,
        [
            f"Plugin {plugin_name} has a valid CANVAS_MANIFEST.json file",
            "Installing plugin:",
            "Posting",
            f"Plugin {plugin_name} successfully installed!",
        ],
        [],
    )


def list_newly_installed_plugin(plugin_name: str) -> tuple[str, int, list[str], list[str]]:
    """Step 3 - list all plugins, including newly installed one"""
    return ("list", 0, [f"{plugin_name}@0.0.1	enabled"], [])


def disable_plugin(plugin_name: str) -> tuple[str, int, list[str], list[str]]:
    """Step 4 - disable plugin"""
    return (
        f"disable {plugin_name}",
        0,
        [f"Disabling {plugin_name} using ", f"Plugin {plugin_name} successfully disabled!"],
        [],
    )


def list_disabled_plugin(plugin_name: str) -> tuple[str, int, list[str], list[str]]:
    """Step 5 - list disabled plugin"""
    return ("list", 0, [f"{plugin_name}@0.0.1	disabled"], [])


def enable_plugin(plugin_name: str) -> tuple[str, int, list[str], list[str]]:
    """Step 6 - enable the disabled plugin"""
    return (
        f"enable {plugin_name}",
        0,
        [f"Enabling {plugin_name} using ", f"Plugin {plugin_name} successfully enabled!"],
        [],
    )


def uninstall_enabled_plugin(plugin_name: str) -> tuple[str, int, list[str], list[str]]:
    """Step 7 - try to uninstall the enabled plugin"""
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
    """Step 8 - disable and then uninstall the plugin"""
    runner.invoke(app, f"disable {plugin_name}")

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
@patch("keyring.get_password")
@patch("keyring.set_password")
@pytest.mark.parametrize(
    "step",
    [
        (list_empty_plugins),
        (install_new_plugin),
        (list_newly_installed_plugin),
        (disable_plugin),
        (list_disabled_plugin),
        (enable_plugin),
        (uninstall_enabled_plugin),
        (uninstall_disabled_plugin),
        (list_empty_plugins),
    ],
)
def test_canvas_list_install_disable_enable_uninstall(
    mock_get_password: MagicMock,
    mock_set_password: MagicMock,
    plugin_name: str,
    create_or_update_config_auth_file_for_testing: None,
    step: Callable,
) -> None:
    """Tests that the Canvas CLI can list, install, disable, enable, and uninstall a plugin"""
    mock_get_password.return_value = None
    mock_set_password.return_value = None

    (command, expected_exit_code, expected_outputs, expected_no_outputs) = step(plugin_name)

    result = runner.invoke(app, command)

    assert result.exit_code == expected_exit_code
    for expected_output in expected_outputs:
        assert expected_output in result.stdout
    for expected_no_output in expected_no_outputs:
        assert expected_no_output not in result.stdout
