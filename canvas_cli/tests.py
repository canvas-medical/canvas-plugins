import os
import shutil
from pathlib import Path
from typing import Any, Generator
from unittest.mock import MagicMock, patch
from urllib.parse import urlparse

import pytest
from typer.testing import CliRunner

import settings
from canvas_cli.apps.auth.utils import CONFIG_PATH

from .main import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def create_or_update_config_auth_file_for_testing(plugin_name: str) -> Generator[Any, Any, Any]:
    """Creates the necessary config file for auth before performing cli tests."""

    host = urlparse(settings.INTEGRATION_TEST_URL).hostname.replace(".canvasmedical.com", "")
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
    if Path(f"./{plugin_name}").exists():
        shutil.rmtree(Path(f"./{plugin_name}"))


@pytest.fixture
def plugin_name() -> str:
    """The plugin name to be used for the canvas cli test"""
    return "cli"


@pytest.fixture
def cli_test_steps(plugin_name: str) -> list[tuple[str, str, int, list[str], list[str]]]:
    """
    The steps for the cli integration test.
    Formatted as (step_name, command, expected_exit_code, expected_outputs, expected_no_outputs).
    """
    return [
        ("List empty plugins", "list", 0, [], [f"{plugin_name}"]),
        (
            "Install new plugin",
            f"install {plugin_name}",
            0,
            [
                f"Plugin {plugin_name} has a valid CANVAS_MANIFEST.json file",
                "Installing plugin:",
                "Posting",
                f"Plugin {plugin_name} successfully installed!",
            ],
            [],
        ),
        ("List newly installed plugin", "list", 0, [f"{plugin_name}@0.0.1	enabled"], []),
        (
            "Disable plugin",
            f"disable {plugin_name}",
            0,
            [f"Disabling {plugin_name} using ", f"Plugin {plugin_name} successfully disabled!"],
            [],
        ),
        ("List disabled plugin", "list", 0, [f"{plugin_name}@0.0.1	disabled"], []),
        (
            "Enable plugin",
            f"enable {plugin_name}",
            0,
            [f"Enabling {plugin_name} using ", f"Plugin {plugin_name} successfully enabled!"],
            [],
        ),
        (
            "Uninstall enabled plugin",
            f"uninstall {plugin_name}",
            1,
            [
                f"Uninstalling {plugin_name} using",
                'Status code 403: {"detail":"Cannot delete an enabled plugin."}',
            ],
            [],
        ),
        ("Disable plugin", f"disable {plugin_name}", 0, [], []),
        (
            "Uninstall disabled plugin",
            f"uninstall {plugin_name}",
            0,
            [
                f"Uninstalling {plugin_name} using",
                f"Plugin {plugin_name} successfully uninstalled!",
            ],
            [],
        ),
        ("List empty plugins again", "list", 0, [], [f"{plugin_name}"]),
    ]


@patch("keyring.get_password")
@patch("keyring.set_password")
@pytest.mark.integtest
def test_canvas_list_install_disable_enable_uninstall(
    mock_get_password: MagicMock,
    mock_set_password: MagicMock,
    plugin_name: str,
    cli_test_steps: list[tuple[str, str, int, list[str], list[str]]],
) -> None:
    """Tests that the Canvas CLI can list, install, disable, enable, and uninstall a plugin"""

    mock_get_password.return_value = None
    mock_set_password.return_value = None

    runner.invoke(app, "init", input=plugin_name)
    protocol = open(f"./{plugin_name}/protocols/my_protocol.py", "w")
    p = [
        "from canvas_sdk.events import EventType\n",
        "from canvas_sdk.protocols import BaseProtocol\n",
        "from logger import log\n",
        "\n",
        "\n",
        "class Protocol(BaseProtocol):\n",
        "\tRESPONDS_TO = EventType.Name(EventType.ASSESS_COMMAND__CONDITION_SELECTED)\n",
        """\tNARRATIVE_STRING = "I was inserted from my plugin's protocol."\n""",
        "\n",
        "\tdef compute(self):\n",
        "\t\tlog.info(self.NARRATIVE_STRING)\n",
        "\t\treturn []\n",
    ]
    protocol.writelines(p)
    protocol.close()

    for (
        step_name,
        command,
        expected_exit_code,
        expected_outputs,
        expected_no_outputs,
    ) in cli_test_steps:
        print(step_name)
        result = runner.invoke(app, command)
        assert result.exit_code == expected_exit_code
        for expected_output in expected_outputs:
            assert expected_output in result.stdout
        for expected_no_ouput in expected_no_outputs:
            assert expected_no_ouput not in result.stdout
