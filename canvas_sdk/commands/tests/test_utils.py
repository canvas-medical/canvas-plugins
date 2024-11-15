import random
import shutil
import string
from contextlib import chdir
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, cast

import pytest
import requests
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


class MaskedValue:
    def __init__(self, value: str) -> None:
        self.value = value

    def __repr__(self) -> str:
        return "MaskedValue(********)"

    def __str___(self) -> str:
        return "*******"


def get_field_type_unformatted(field_props: dict[str, Any]) -> str:
    if t := field_props.get("type"):
        return field_props.get("format") or t

    first_in_union: dict = field_props.get("anyOf", field_props.get("allOf"))[0]
    if "$ref" in first_in_union:
        return first_in_union["$ref"].split("#/$defs/")[-1]
    return first_in_union.get("format") or first_in_union["type"]


def get_field_type(field_props: dict) -> str:
    return get_field_type_unformatted(field_props).replace("-", "").replace("array", "list")


def random_string() -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=7))


def fake(field_props: dict, Command: type[_BaseCommand]) -> Any:
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
    if t[0].isupper():
        return random.choice([e for e in getattr(Command, t)])


def raises_wrong_type_error(
    Command: type[_BaseCommand],
    field: str,
) -> None:
    field_props = Command.model_json_schema()["properties"][field]
    field_type = get_field_type(field_props)
    wrong_field_type = "integer" if field_type == "string" else "string"

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

    assert f"1 validation error for {Command.__name__}\n{field}" in err_msg1
    assert f"1 validation error for {Command.__name__}\n{field}" in err_msg2

    field_type = (
        "dictionary" if field_type == "Coding" or field_type == "ClinicalQuantity" else field_type
    )
    if field_type == "number":
        assert f"Input should be an instance of Decimal" in err_msg1
        assert f"Input should be an instance of Decimal" in err_msg2
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

    protocol = open(f"./custom-plugins/{plugin_name}/protocols/my_protocol.py", "w")
    protocol.write(protocol_code)
    protocol.close()


def install_plugin(plugin_name: str, token: MaskedValue) -> None:
    requests.post(
        plugin_url(cast(str, settings.INTEGRATION_TEST_URL)),
        data={"is_enabled": True},
        files={"package": open(_build_package(Path(f"./custom-plugins/{plugin_name}")), "rb")},
        headers={"Authorization": f"Bearer {token.value}"},
    )


def trigger_plugin_event(token: MaskedValue) -> None:
    requests.post(
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


def get_original_note_body_commands(new_note_id: int, token: MaskedValue) -> list[str]:
    original_note = requests.get(
        f"{settings.INTEGRATION_TEST_URL}/api/Note/{new_note_id}",
        headers={
            "Authorization": f"Bearer {token.value}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    ).json()

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
    # clean up
    if Path(f"./custom-plugins/{plugin_name}").exists():
        shutil.rmtree(Path(f"./custom-plugins/{plugin_name}"))

    # disable
    requests.patch(
        plugin_url(cast(str, settings.INTEGRATION_TEST_URL), plugin_name),
        data={"is_enabled": False},
        headers={
            "Authorization": f"Bearer {token.value}",
        },
    )
    # delete
    requests.delete(
        plugin_url(cast(str, settings.INTEGRATION_TEST_URL), plugin_name),
        headers={"Authorization": f"Bearer {token.value}"},
    )


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
    return requests.post(
        f"{settings.INTEGRATION_TEST_URL}/api/Note/", headers=headers, json=data
    ).json()


def get_token() -> MaskedValue:
    return MaskedValue(
        requests.post(
            f"{settings.INTEGRATION_TEST_URL}/auth/token/",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "client_credentials",
                "client_id": settings.INTEGRATION_TEST_CLIENT_ID,
                "client_secret": settings.INTEGRATION_TEST_CLIENT_SECRET,
            },
        ).json()["access_token"]
    )
