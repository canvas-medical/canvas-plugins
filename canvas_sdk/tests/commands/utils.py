import ast
import inspect
import json
from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from typing import Any, TypedDict, cast

import requests
from django.conf import settings
from typer.testing import CliRunner

from canvas_cli.main import app
from canvas_generated.messages.events_pb2 import Event
from canvas_sdk import commands
from canvas_sdk.commands import __all__ as commands_registry
from canvas_sdk.commands.base import _BaseCommand
from canvas_sdk.tests.shared import MaskedValue, trigger_plugin_event

TEST_PLUGINS_DIR = Path(__file__).parent


COMMANDS: list[type[_BaseCommand]] = [
    getattr(commands, attr_name) for attr_name in commands_registry
]

CommandCode = TypedDict("CommandCode", {"class": type[_BaseCommand], "data": str})


def command_event_prefix(command: type[_BaseCommand]) -> str:
    """Get the event prefix for the command events."""
    if command.Meta.key == "hpi":
        return "HISTORY_OF_PRESENT_ILLNESS"
    elif command.Meta.key == "exam":
        return "PHYSICAL_EXAM"
    else:
        return command.constantized_key()


def get_command(command_uuid: str, token: MaskedValue) -> dict:
    """Get the command."""
    url = f"{settings.INTEGRATION_TEST_URL}/core/api/v1/commands/{command_uuid}/"

    return requests.get(url, headers={"Authorization": f"Bearer {token.value}"}).json()


def originate_command(
    command_key: str,
    note_uuid: str,
    token: MaskedValue,
) -> dict:
    """Create a command in the given note."""
    data = {"noteKey": note_uuid, "schemaKey": command_key}
    url = f"{settings.INTEGRATION_TEST_URL}/core/api/v1/commands/"

    return requests.post(url, headers={"Authorization": f"Bearer {token.value}"}, data=data).json()


def get_command_fields(
    command_uuid: str,
    token: MaskedValue,
) -> list[dict[str, str]]:
    """Get the command fields."""
    url = f"{settings.INTEGRATION_TEST_URL}/core/api/v1/commands/{command_uuid}/fields/"

    return requests.get(url, headers={"Authorization": f"Bearer {token.value}"}).json()["fields"]


def get_commands_in_note(
    note_id: int,
    token: MaskedValue,
    command_key: str | None = None,
    command_uuid: str | None = None,
) -> list[dict[str, Any]]:
    """Get the commands from the original note body."""
    response = requests.get(
        f"{settings.INTEGRATION_TEST_URL}/api/Note/{note_id}",
        headers={
            "Authorization": f"Bearer {token.value}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    response.raise_for_status()

    original_note = response.json()

    body = original_note["body"]
    return [
        line
        for line in body
        if "data" in line
        and "commandUuid" in line["data"]
        and "id" in line["data"]
        and line["type"] == "command"
        and ((command_key and line["value"] == command_key) or not command_key)
        and ((command_uuid and line["data"]["commandUuid"] == command_uuid) or not command_uuid)
    ]


def write_protocol_code(
    cli_runner: CliRunner,
    plugin_path: Path,
    commands: list[CommandCode],
) -> None:
    """Test that the protocol code is written correctly."""
    imports = ", ".join(
        [cast(type[_BaseCommand], command.get("class")).__name__ for command in commands]
    )

    imports = f"""from canvas_sdk.commands import {imports}
from canvas_sdk.commands.commands.allergy import Allergen, AllergenType
from datetime import datetime, date
from canvas_sdk.v1.data import Condition
from canvas_sdk.protocols import BaseProtocol
"""

    protocol_classes = []

    for command in commands:
        command_cls = command["class"]
        data = command["data"]
        event_prefix = command_event_prefix(command_cls)
        protocol_classes.append(f"""


class Originate{command_cls.__name__}Protocol(BaseProtocol):
    RESPONDS_TO = "{event_prefix}_COMMAND__POST_INSERTED_INTO_NOTE"
    def compute(self):
        is_ci = self.event.context.get("ci_originate")
        if not is_ci:
            return []

        note = self.event.context["note"]

        if is_ci.get("empty"):
            return [{command_cls.__name__}(note_uuid=note["uuid"]).originate()]
        else:
            return [{command_cls.__name__}(note_uuid=note["uuid"], **{data}).originate()]


class Edit{command_cls.__name__}Protocol(BaseProtocol):
    RESPONDS_TO = "{event_prefix}_COMMAND__POST_INSERTED_INTO_NOTE"
    def compute(self):
        is_ci = self.event.context.get("ci_edit")
        if not is_ci:
            return []
        return [{command_cls.__name__}(command_uuid=self.event.target.id, **{data}).edit()]


class Commit{command_cls.__name__}Protocol(BaseProtocol):
    RESPONDS_TO = "{event_prefix}_COMMAND__POST_INSERTED_INTO_NOTE"
    def compute(self):
        is_ci = self.event.context.get("ci_commit")
        if not is_ci:
            return []
        return [{command_cls.__name__}(command_uuid=self.event.target.id).commit()]
""")

    protocol_code = f"{imports}{''.join(protocol_classes)}"

    with chdir(plugin_path.parent):
        cli_runner.invoke(app, "init", input=plugin_path.name)

    with open(plugin_path / "protocols" / "my_protocol.py", "w") as protocol:
        protocol.write(protocol_code)

    protocols = []

    for command in commands:
        command_cls = command["class"]
        originate = {
            "class": f"{plugin_path.name}.protocols.my_protocol:Originate{command_cls.__name__}Protocol",
            "description": "A protocol that does xyz...",
            "data_access": {"event": "", "read": [], "write": []},
        }
        edit = {
            "class": f"{plugin_path.name}.protocols.my_protocol:Edit{command_cls.__name__}Protocol",
            "description": "A protocol that does xyz...",
            "data_access": {"event": "", "read": [], "write": []},
        }
        commit = {
            "class": f"{plugin_path.name}.protocols.my_protocol:Commit{command_cls.__name__}Protocol",
            "description": "A protocol that does xyz...",
            "data_access": {"event": "", "read": [], "write": []},
        }
        protocols.append(originate)
        protocols.append(edit)
        protocols.append(commit)

    manifest = {
        "sdk_version": "0.1.4",
        "plugin_version": "0.0.1",
        "name": plugin_path.name,
        "description": "Edit the description in CANVAS_MANIFEST.json",
        "components": {
            "protocols": protocols,
            "commands": [],
            "content": [],
            "effects": [],
            "views": [],
        },
        "secrets": [],
        "tags": {},
        "references": [],
        "license": "",
        "diagram": True,
        "readme": "./README.md",
    }

    with open(plugin_path / "CANVAS_MANIFEST.json", "w") as manifest_file:
        json.dump(manifest, manifest_file)


def extract_return_statement(func: Callable) -> str:
    """Extracts only the return statement from a function's source."""
    source = inspect.getsource(func)
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.Return):
            return ast.unparse(node.value).strip() if node.value else ""

    return ""


def trigger_originate(
    token: MaskedValue,
    command_cls: type[_BaseCommand],
    note_uuid: str,
    empty: bool = False,
) -> None:
    """Trigger the plugin event."""
    event = Event(
        type=f"{command_event_prefix(command_cls)}_COMMAND__POST_INSERTED_INTO_NOTE",
        context=json.dumps({"note": {"uuid": note_uuid}, "ci_originate": {"empty": empty}}),
    )
    trigger_plugin_event(event, token)


def trigger_edit_command(
    command_uuid: str,
    command_cls: type[_BaseCommand],
    token: MaskedValue,
) -> None:
    """Trigger the plugin event."""
    event = Event(
        type=f"{command_event_prefix(command_cls)}_COMMAND__POST_INSERTED_INTO_NOTE",
        target=command_uuid,
        context=json.dumps({"ci_edit": True}),
    )
    trigger_plugin_event(event, token)


def trigger_commit_command(
    command_uuid: str,
    command_cls: type[_BaseCommand],
    token: MaskedValue,
) -> None:
    """Trigger the plugin event."""
    event = Event(
        type=f"{command_event_prefix(command_cls)}_COMMAND__POST_INSERTED_INTO_NOTE",
        target=command_uuid,
        context=json.dumps({"ci_commit": True}),
    )
    trigger_plugin_event(event, token)
