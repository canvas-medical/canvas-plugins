import ast
import inspect
import json
import sys
from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from typing import Any, cast

if sys.version_info >= (3, 12):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

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

# SOME COMMANDS MIGHT NOT BE IN PRODUCTION, SO WE NEED TO SKIP INTEGTEST FOR THEM
COMMANDS_TO_SKIP = [
    "ImmunizeCommand",
    "LabReviewCommand",
    "ReferralReviewCommand",
    "ImagingReviewCommand",
    "UncategorizedDocumentReviewCommand",
    "CustomCommand",
]


COMMANDS: list[type[_BaseCommand]] = [
    getattr(commands, attr_name)
    for attr_name in commands_registry
    if attr_name not in COMMANDS_TO_SKIP
]

CommandCode = TypedDict("CommandCode", {"class": type[_BaseCommand], "data": str})


class NoteCommand(TypedDict):
    """A command line in a note body."""

    command_uuid: str
    key: str


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


def _commands_from_body(body: list[dict[str, Any]]) -> list[NoteCommand]:
    """Extract the commands from a version 1 note body, which is a list of lines."""
    return [
        NoteCommand(command_uuid=line["data"]["commandUuid"], key=line["value"])
        for line in body
        if line["type"] == "command"
        and "data" in line
        and "commandUuid" in line["data"]
        and "id" in line["data"]
    ]


def _commands_from_body_content(
    body_content: dict[str, dict[str, Any]],
    body_order: list[str],
) -> list[NoteCommand]:
    """Extract the commands from a version 2 note body, which is keyed by line uuid.

    A command's line uuid is its command uuid, and `body_order` holds the line
    order, so the commands come back in the order they appear in the note.
    """
    return [
        NoteCommand(command_uuid=line_uuid, key=body_content[line_uuid]["value"])
        for line_uuid in body_order
        if body_content.get(line_uuid, {}).get("type") == "command"
    ]


def get_commands_in_note(
    note_id: int,
    token: MaskedValue,
    command_key: str | None = None,
    command_uuid: str | None = None,
) -> list[NoteCommand]:
    """Get the commands in the note body, optionally filtered by key or command uuid."""
    response = requests.get(
        f"{settings.INTEGRATION_TEST_URL}/api/Note/{note_id}",
        headers={
            "Authorization": f"Bearer {token.value}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    response.raise_for_status()

    note = response.json()

    commands = (
        _commands_from_body_content(note["bodyContent"], note["bodyOrder"])
        if note.get("version") == 2
        else _commands_from_body(note["body"])
    )

    return [
        command
        for command in commands
        if (command_key is None or command["key"] == command_key)
        and (command_uuid is None or command["command_uuid"] == command_uuid)
    ]


def write_handler_code(
    cli_runner: CliRunner,
    plugin_path: Path,
    commands: list[CommandCode],
) -> None:
    """Write handler code for testing command functionality."""
    imports = ", ".join(
        [cast(type[_BaseCommand], command.get("class")).__name__ for command in commands]
    )

    imports = f"""from canvas_sdk.commands import {imports}
from canvas_sdk.commands.commands.allergy import Allergen, AllergenType
from datetime import datetime, date
from canvas_sdk.v1.data import Condition
from canvas_sdk.handlers import BaseHandler
"""

    handler_classes = []

    for command in commands:
        command_cls = command["class"]
        data = command["data"]
        event_prefix = command_event_prefix(command_cls)
        handler_classes.append(f"""


class Originate{command_cls.__name__}Handler(BaseHandler):
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


class Edit{command_cls.__name__}Handler(BaseHandler):
    RESPONDS_TO = "{event_prefix}_COMMAND__POST_INSERTED_INTO_NOTE"
    def compute(self):
        is_ci = self.event.context.get("ci_edit")
        if not is_ci:
            return []
        return [{command_cls.__name__}(command_uuid=self.event.target.id, **{data}).edit()]


class Commit{command_cls.__name__}Handler(BaseHandler):
    RESPONDS_TO = "{event_prefix}_COMMAND__POST_INSERTED_INTO_NOTE"
    def compute(self):
        is_ci = self.event.context.get("ci_commit")
        if not is_ci:
            return []
        return [{command_cls.__name__}(command_uuid=self.event.target.id).commit()]
""")

    handler_code = f"{imports}{''.join(handler_classes)}"

    with chdir(plugin_path.parent):
        cli_runner.invoke(app, "init", input=plugin_path.name)

    package_name = plugin_path.name.replace("-", "_")

    # Write handler code to the handlers directory (created by canvas init)
    with open(plugin_path / package_name / "handlers" / "event_handlers.py", "w") as handler_file:
        handler_file.write(handler_code)

    handlers = []

    for command in commands:
        command_cls = command["class"]
        originate = {
            "class": f"{package_name}.handlers.event_handlers:Originate{command_cls.__name__}Handler",
            "description": f"Handler that originates {command_cls.__name__}",
        }
        edit = {
            "class": f"{package_name}.handlers.event_handlers:Edit{command_cls.__name__}Handler",
            "description": f"Handler that edits {command_cls.__name__}",
        }
        commit = {
            "class": f"{package_name}.handlers.event_handlers:Commit{command_cls.__name__}Handler",
            "description": f"Handler that commits {command_cls.__name__}",
        }
        handlers.append(originate)
        handlers.append(edit)
        handlers.append(commit)

    manifest = {
        "sdk_version": "0.1.4",
        "plugin_version": "0.0.1",
        "name": plugin_path.name,
        "description": "Edit the description in CANVAS_MANIFEST.json",
        "components": {
            "handlers": handlers,
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

    with open(plugin_path / package_name / "CANVAS_MANIFEST.json", "w") as manifest_file:
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
