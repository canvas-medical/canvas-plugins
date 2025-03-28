import random
import shutil
import string
import threading
from contextlib import chdir
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, cast
from urllib.parse import urlparse

import pytest
import requests
import websocket
from pydantic import ValidationError
from typer.testing import CliRunner

import settings
from canvas_cli.apps.plugin.plugin import _build_package, plugin_url
from canvas_cli.main import app
from canvas_sdk.commands import (
    AssessCommand,
    DiagnoseCommand,
    GoalCommand,
    HistoryOfPresentIllnessCommand,
    MedicationStatementCommand,
    PlanCommand,
    PrescribeCommand,
    QuestionnaireCommand,
    ReasonForVisitCommand,
    StopMedicationCommand,
    UpdateGoalCommand,
)
from canvas_sdk.commands.base import _BaseCommand
from canvas_sdk.commands.constants import ClinicalQuantity, Coding

runner = CliRunner()


class WrongType:
    """A type to yield ValidationErrors in tests."""

    wrong_field: str


class MaskedValue:
    """A class to mask sensitive values in tests."""

    def __init__(self, value: str) -> None:
        self.value = value

    def __repr__(self) -> str:
        return "MaskedValue(********)"

    def __str___(self) -> str:
        return "*******"


def get_field_type_unformatted(field_props: dict[str, Any]) -> str:
    """Get the unformatted field type from the field properties."""
    if t := field_props.get("type"):
        return field_props.get("format") or t

    first_in_union: dict = field_props.get("anyOf", field_props.get("allOf"))[0]
    if "$ref" in first_in_union:
        return first_in_union["$ref"].split("#/$defs/")[-1]
    return first_in_union.get("format") or first_in_union["type"]


def get_field_type(field_props: dict) -> str:
    """Get the field type from the field properties."""
    return get_field_type_unformatted(field_props).replace("-", "").replace("array", "list")


def random_string() -> str:
    """Generate a random string."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=7))


def fake(field_props: dict, Command: type[_BaseCommand]) -> Any:
    """Generate a fake value for a field."""
    t = get_field_type(field_props)
    match t:
        case "string":
            return random_string()
        case "integer":
            return random.randint(1, 10)
        case "datetime":
            return datetime.now()
        case "boolean":
            return random.choice([True, False])
        case "number":
            return Decimal(random.randrange(1, 200))
        case "array":
            num_items = random.randint(0, 5)
            item_props = field_props["anyOf"][0]["items"]
            return [fake(item_props, Command) for i in range(num_items)]
        case "list":
            num_items = random.randint(0, field_props.get("maxItems", 5))
            item_props = field_props.get("items")
            return [fake(item_props, Command) for i in range(num_items)] if item_props else []
        case "Coding":
            return Coding(system=random_string(), code=random_string(), display=random_string())
        case "ClinicalQuantity":
            return ClinicalQuantity(representative_ndc="ndc", ncpdp_quantity_qualifier_code="code")
        case "WrongType":
            return WrongType()
    if t[0].isupper():
        return random.choice(list(getattr(Command, t)))


def raises_wrong_type_error(
    Command: type[_BaseCommand],
    field: str,
) -> None:
    """Test that the correct error is raised when the wrong type is passed to a field."""
    field_props = Command.model_json_schema()["properties"][field]
    field_type = get_field_type(field_props)

    wrong_field_type = "WrongType"

    with pytest.raises(ValidationError) as e1:
        err_kwargs = {field: fake({"type": wrong_field_type}, Command)}
        Command(**err_kwargs)
    err_msg1 = repr(e1.value)

    valid_kwargs = {field: fake(field_props, Command)}
    cmd = Command(**valid_kwargs)
    err_value = fake({"type": wrong_field_type}, Command)
    with pytest.raises(ValidationError) as e2:
        setattr(cmd, field, err_value)
    err_msg2 = repr(e2.value)

    assert "validation error" in err_msg1
    assert f"{Command.__name__}\n{field}" in err_msg1

    assert "validation error" in err_msg2
    assert f"{Command.__name__}\n{field}" in err_msg1

    field_type = (
        "dictionary" if field_type == "Coding" or field_type == "ClinicalQuantity" else field_type
    )
    if field_type == "number":
        assert "Input should be an instance of Decimal" in err_msg1
        assert "Input should be an instance of Decimal" in err_msg2
    elif field_type[0].isupper():
        assert f"Input should be an instance of {Command.__name__}.{field_type}" in err_msg1
        assert f"Input should be an instance of {Command.__name__}.{field_type}" in err_msg2
    else:
        assert f"Input should be a valid {field_type}" in err_msg1
        assert f"Input should be a valid {field_type}" in err_msg2


def raises_none_error_for_effect_method(
    Command: type[_BaseCommand],
    method: str,
) -> None:
    """Test that the correct error is raised when a required field is None for an effect method."""
    cmd_name = Command.__name__
    cmd_name_article = "an" if cmd_name.startswith(("A", "E", "I", "O", "U")) else "a"

    cmd = Command()
    method_required_fields = cmd._get_effect_method_required_fields(method)
    with pytest.raises(ValidationError) as e:
        getattr(cmd, method)()
    e_msg = repr(e.value)
    missing_fields = [field for field in method_required_fields if getattr(cmd, field) is None]
    num_errs = len(missing_fields)
    assert f"{num_errs} validation error{'s' if num_errs > 1 else ''} for {cmd_name}" in e_msg

    for f in missing_fields:
        assert (
            f"Field '{f}' is required to {method.replace('_', ' ')} {cmd_name_article} {cmd_name} [type=missing, input_value=None, input_type=NoneType]"
            in e_msg
        )


def write_protocol_code(
    note_uuid: str, plugin_name: str, commands: list[type[_BaseCommand]]
) -> None:
    """Test that the protocol code is written correctly."""
    imports = ", ".join([c.__name__ for c in commands])
    effects = ", ".join([f"{c.__name__}(note_uuid='{note_uuid}').originate()" for c in commands])

    protocol_code = f"""from canvas_sdk.commands import {imports}
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol

class Protocol(BaseProtocol):
    RESPONDS_TO = EventType.Name(EventType.ENCOUNTER_CREATED)
    def compute(self):
        return [{effects}]
"""

    with chdir(Path("./custom-plugins")):
        runner.invoke(app, "init", input=plugin_name)

    with open(f"./custom-plugins/{plugin_name}/protocols/my_protocol.py", "w") as protocol:
        protocol.write(protocol_code)


def install_plugin(plugin_name: str, token: MaskedValue) -> None:
    """Install a plugin."""
    with open(_build_package(Path(f"./custom-plugins/{plugin_name}")), "rb") as package:
        response = requests.post(
            plugin_url(cast(str, settings.INTEGRATION_TEST_URL)),
            data={"is_enabled": True},
            files={"package": package},
            headers={"Authorization": f"Bearer {token.value}"},
        )
        response.raise_for_status()


def trigger_plugin_event(token: MaskedValue) -> None:
    """Trigger a plugin event."""
    response = requests.post(
        f"{settings.INTEGRATION_TEST_URL}/api/Note/",
        headers={
            "Authorization": f"Bearer {token.value}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        json={
            "patient": 2,
            "provider": 1,
            "note_type": "office",
            "note_type_version": 1,
            "lastModifiedBySessionKey": "8fee3c03a525cebee1d8a6b8e63dd4dg",
        },
    )
    response.raise_for_status()


def get_original_note_body_commands(new_note_id: int, token: MaskedValue) -> list[str]:
    """Get the commands from the original note body."""
    response = requests.get(
        f"{settings.INTEGRATION_TEST_URL}/api/Note/{new_note_id}",
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
        line["value"]
        for line in body
        if "data" in line
        and "commandUuid" in line["data"]
        and "id" in line["data"]
        and line["type"] == "command"
    ]


def clean_up_files_and_plugins(plugin_name: str, token: MaskedValue) -> None:
    """Clean up the files and plugins."""
    # clean up
    if Path(f"./custom-plugins/{plugin_name}").exists():
        shutil.rmtree(Path(f"./custom-plugins/{plugin_name}"))

    # disable
    response = requests.patch(
        plugin_url(cast(str, settings.INTEGRATION_TEST_URL), plugin_name),
        data={"is_enabled": False},
        headers={
            "Authorization": f"Bearer {token.value}",
        },
    )
    response.raise_for_status()

    # delete
    response = requests.delete(
        plugin_url(cast(str, settings.INTEGRATION_TEST_URL), plugin_name),
        headers={"Authorization": f"Bearer {token.value}"},
    )
    response.raise_for_status()


# For reuse with the protocol code
COMMANDS: list[type[_BaseCommand]] = [
    AssessCommand,
    DiagnoseCommand,
    GoalCommand,
    HistoryOfPresentIllnessCommand,
    MedicationStatementCommand,
    PlanCommand,
    PrescribeCommand,
    QuestionnaireCommand,
    ReasonForVisitCommand,
    StopMedicationCommand,
    UpdateGoalCommand,
]


def create_new_note(token: MaskedValue) -> dict:
    """Create a new note."""
    headers = {
        "Authorization": f"Bearer {token.value}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    data = {
        "patient": 1,
        "provider": 1,
        "note_type": "office",
        "note_type_version": 1,
        "lastModifiedBySessionKey": "8fee3c03a525cebee1d8a6b8e63dd4dg",
    }
    response = requests.post(
        f"{settings.INTEGRATION_TEST_URL}/api/Note/", headers=headers, json=data
    )
    response.raise_for_status()
    return response.json()


def get_token() -> MaskedValue:
    """Get a valid token."""
    response = requests.post(
        f"{settings.INTEGRATION_TEST_URL}/auth/token/",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": settings.INTEGRATION_TEST_CLIENT_ID,
            "client_secret": settings.INTEGRATION_TEST_CLIENT_SECRET,
        },
    )
    response.raise_for_status()

    return MaskedValue(response.json()["access_token"])


def wait_for_log(
    host: str, token: str, message: str
) -> tuple[threading.Event, threading.Thread, websocket.WebSocketApp]:
    """Wait for a specific log message."""
    hostname = cast(str, urlparse(host).hostname)
    instance = hostname.removesuffix(".canvasmedical.com")

    websocket_uri = f"wss://logs.console.canvasmedical.com/{instance}?token={token}"

    connected_event = threading.Event()
    message_received_event = threading.Event()

    def _on_message(ws: websocket.WebSocket, received_message: str) -> None:
        try:
            if "Log stream connected" in received_message:
                connected_event.set()
            if message.lower() in received_message.lower():
                message_received_event.set()
                ws.close()
        except Exception as ex:
            print(f"Error processing message: {ex}")

    def _on_error(ws: websocket.WebSocket, error: str) -> None:
        print(f"WebSocket error: {error}")

    ws = websocket.WebSocketApp(
        websocket_uri,
        on_message=_on_message,
        on_error=_on_error,
    )

    thread = threading.Thread(target=ws.run_forever)
    thread.start()

    timeout_not_hit = connected_event.wait(timeout=5.0)
    if not timeout_not_hit:
        ws.close()
    assert timeout_not_hit, "connection timeout hit"

    return message_received_event, thread, ws
