import json
from collections.abc import Generator
from datetime import date
from time import sleep
from typing import Any

import pytest
from typer.testing import CliRunner

from canvas_generated.messages.events_pb2 import Event
from canvas_sdk.commands import AllergyCommand, GoalCommand
from canvas_sdk.commands.base import _BaseCommand
from canvas_sdk.commands.commands.allergy import Allergen, AllergenType
from canvas_sdk.tests.commands.utils import (
    COMMANDS,
    CommandCode,
    command_event_prefix,
    extract_return_statement,
    get_command,
    get_command_fields,
    get_commands_in_note,
    originate_command,
    write_protocol_code,
)
from canvas_sdk.tests.utils import (
    MaskedValue,
    clean_up_files_and_plugins,
    create_note,
    install_plugin,
    trigger_plugin_event,
)


def allergy() -> dict[str, Any]:
    """Allergy Command for testing."""
    return {
        "allergy": Allergen(concept_id=900208, concept_type=AllergenType.ALLERGEN_GROUP),
        "severity": AllergyCommand.Severity.MILD,
        "narrative": "Test",
        "approximate_date": date(2023, 1, 1),
    }


def plan() -> dict[str, Any]:
    """Plan Command for testing."""
    return {"narrative": "Test"}


def goal() -> dict[str, Any]:
    """Goal Command for testing."""
    return {
        "goal_statement": "Test",
        "start_date": date(2023, 1, 1),
        "due_date": date(2024, 1, 1),
        "achievement_status": GoalCommand.AchievementStatus.IN_PROGRESS,
        "priority": GoalCommand.Priority.HIGH,
        "progress": "in progress",
    }


@pytest.fixture(params=COMMANDS)
def command_cls(request: Any) -> type[_BaseCommand]:
    """The command to be tested."""
    return request.param


@pytest.fixture(scope="session")
def install_plugin_commands(
    cli_runner: CliRunner,
    token: MaskedValue,
) -> Generator[None, None, None]:
    """Write the protocol code, install the plugin, and clean up after the test."""
    plugin_name = "commands"
    commands: list[CommandCode] = []
    for command_cls in COMMANDS:
        get_command_data = globals().get(command_cls.Meta.key)
        data = extract_return_statement(get_command_data) if get_command_data else "{}"
        commands.append(CommandCode(**{"data": data, "class": command_cls}))

    write_protocol_code(cli_runner, plugin_name, commands)
    install_plugin(plugin_name, token)
    sleep(1)

    yield

    clean_up_files_and_plugins(plugin_name, token)


@pytest.fixture(scope="module")
def note_for_originating_commands(token: MaskedValue) -> dict:
    """The note to be used for originating commands."""
    return create_note(token)


@pytest.fixture(scope="module")
def note_for_originating_empty_commands(token: MaskedValue) -> dict:
    """The note to be used for originating commands."""
    return create_note(token)


@pytest.fixture(scope="module")
def note_for_editing_commands(token: MaskedValue) -> dict:
    """The note to be used for editing commands."""
    return create_note(token)


@pytest.fixture(scope="module")
def note_for_schema(token: MaskedValue) -> dict:
    """The note to be used for command schema tests."""
    return create_note(token)


@pytest.fixture
def command_data(command_cls: type[_BaseCommand]) -> dict[str, Any]:
    """The command data to be used for command schema tests."""
    get_command_data = globals().get(command_cls.Meta.key)
    if not get_command_data:
        pytest.skip(f"No command values found for '{command_cls.Meta.key}'")

    return get_command_data()


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


@pytest.fixture
def command_api_fields(
    token: MaskedValue, note_for_schema: dict, command_cls: type[_BaseCommand]
) -> list[dict[str, Any]]:
    """Return the fields of a command."""
    response = originate_command(
        command_key=command_cls.Meta.key,
        note_uuid=note_for_schema["externallyExposableId"],
        token=token,
    )

    command_uuid = response["uuid"]

    return get_command_fields(command_uuid, token)


def test_command_has_commit_required_fields(command_cls: type[_BaseCommand]) -> None:
    """Test that the command schema has the commit required fields."""
    for field in getattr(command_cls.Meta, "commit_required_fields", ()):
        assert field in command_cls.model_fields


@pytest.mark.integtest
def test_command_commit_required_fields_matches_command_api(
    command_api_fields: list[dict[str, Any]], command_cls: type[_BaseCommand]
) -> None:
    """Test that the command schema's commit required fields match the command API."""
    schema_fields = command_cls.command_schema()

    for api_field in command_api_fields:
        if api_field["required"]:
            api_field_name = api_field["name"]
            assert api_field_name in schema_fields, (
                f"Expected field '{api_field_name}' to be present."
            )
            assert schema_fields[api_field_name]["required"] is True, (
                f"Expected field '{api_field_name}' to be required."
            )


@pytest.mark.integtest
def test_plugin_originates_command_in_note(
    token: MaskedValue,
    install_plugin_commands: None,
    note_for_originating_commands: dict,
    command_cls: type[_BaseCommand],
    command_data: dict[str, Any],
) -> None:
    """Test that commands are successfully originated in a note via plugin."""
    trigger_originate(token, command_cls, note_for_originating_commands["externallyExposableId"])
    commands_in_note = get_commands_in_note(
        note_id=note_for_originating_commands["id"], token=token, command_key=command_cls.Meta.key
    )

    assert len(commands_in_note) == 1

    command_uuid = commands_in_note[0]["data"]["commandUuid"]
    command = get_command(command_uuid, token=token)

    schema = command_cls.model_json_schema()

    for field in command_data:
        api_field_name = schema["properties"][field].get("commands_api_name", field)
        assert command["data"][api_field_name], f"Expected field '{api_field_name}' to be present."


@pytest.mark.integtest
def test_plugin_originates_empty_command_in_note(
    token: MaskedValue,
    install_plugin_commands: None,
    note_for_originating_empty_commands: dict,
    command_cls: type[_BaseCommand],
) -> None:
    """Test that commands are successfully originated in a note via plugin."""
    trigger_originate(
        token, command_cls, note_for_originating_empty_commands["externallyExposableId"], empty=True
    )
    commands_in_note = get_commands_in_note(
        note_id=note_for_originating_empty_commands["id"],
        token=token,
        command_key=command_cls.Meta.key,
    )

    assert len(commands_in_note) == 1


@pytest.mark.integtest
def test_plugin_edits_command(
    token: MaskedValue,
    install_plugin_commands: None,
    note_for_editing_commands: dict,
    command_cls: type[_BaseCommand],
    command_data: dict[str, Any],
) -> None:
    """Test that commands are successfully edited via plugin."""
    command = originate_command(
        command_key=command_cls.Meta.key,
        note_uuid=note_for_editing_commands["externallyExposableId"],
        token=token,
    )

    trigger_edit_command(
        command_uuid=command["uuid"],
        command_cls=command_cls,
        token=token,
    )
    command = get_command(command["uuid"], token=token)

    schema = command_cls.model_json_schema()

    for field in command_data:
        api_field_name = schema["properties"][field].get("commands_api_name", field)
        assert command["data"][api_field_name], f"Expected field '{api_field_name}' to be present."


@pytest.mark.integtest
def test_plugin_commits_command(
    token: MaskedValue,
    install_plugin_commands: None,
    note_for_editing_commands: dict,
    command_cls: type[_BaseCommand],
    command_data: dict[str, Any],
) -> None:
    """Test that commands are successfully edited via plugin."""
    command = originate_command(
        command_key=command_cls.Meta.key,
        note_uuid=note_for_editing_commands["externallyExposableId"],
        token=token,
    )

    trigger_edit_command(
        command_uuid=command["uuid"],
        command_cls=command_cls,
        token=token,
    )

    trigger_commit_command(
        command_uuid=command["uuid"],
        command_cls=command_cls,
        token=token,
    )

    command = get_command(command["uuid"], token=token)

    assert command["state"] == "committed", (
        f"Expected command state to be 'committed', but got '{command['state']}'"
    )
