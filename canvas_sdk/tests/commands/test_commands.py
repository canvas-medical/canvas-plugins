from collections.abc import Generator
from datetime import date
from pathlib import Path
from time import sleep
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from canvas_sdk.commands import (
    AllergyCommand,
    AssessCommand,
    ChartSectionReviewCommand,
    GoalCommand,
)
from canvas_sdk.commands.base import _BaseCommand
from canvas_sdk.commands.commands.allergy import Allergen, AllergenType
from canvas_sdk.tests.commands.utils import (
    COMMANDS,
    CommandCode,
    extract_return_statement,
    get_command,
    get_commands_in_note,
    originate_command,
    trigger_commit_command,
    trigger_edit_command,
    trigger_originate,
    write_protocol_code,
)
from canvas_sdk.tests.shared import (
    MaskedValue,
    clean_up_files_and_plugins,
    create_note,
    install_plugin,
)
from canvas_sdk.v1.data import Condition

# some commands can't be originated without any content
EMPTY_COMMAND_NOT_ALLOWED = ["chartSectionReview"]


def allergy() -> dict[str, Any]:
    """Allergy Command for testing."""
    return {
        "allergy": Allergen(concept_id=900208, concept_type=AllergenType.ALLERGEN_GROUP),
        "severity": AllergyCommand.Severity.MILD,
        "narrative": "Test",
        "approximate_date": date(2023, 1, 1),
    }


def assess() -> dict[str, Any]:
    """Assess Command for testing."""
    return {
        "condition_id": Condition.objects.active().filter(patient_id=1).first().id,  # type: ignore
        "background": "Severe pain",
        "status": AssessCommand.Status.STABLE,
        "narrative": "The patient has improved.",
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


def chart_section_review() -> dict[str, Any]:
    """Chart Section Review Command for testing."""
    return {"section": ChartSectionReviewCommand.Sections.MEDICATIONS}


@pytest.fixture(scope="module", autouse=True)
def patch_condition() -> Generator[None, None, None]:
    """Patch the Condition model to return a mock queryset."""
    with patch.object(Condition.objects, "active") as mock_active:
        mock_qs = MagicMock()
        mock_first = MagicMock()
        mock_first.id = 1

        mock_qs.filter.return_value.first.return_value = mock_first
        mock_active.return_value = mock_qs

        yield


@pytest.fixture(params=COMMANDS)
def command_cls(request: Any) -> type[_BaseCommand]:
    """The command to be tested."""
    return request.param


@pytest.fixture(scope="session")
def install_plugin_commands(
    cli_runner: CliRunner,
    token: MaskedValue,
    integration_tests_plugins_dir: Path,
) -> Generator[None, None, None]:
    """Write the protocol code, install the plugin, and clean up after the test."""
    plugin_path = integration_tests_plugins_dir / "commands"
    commands: list[CommandCode] = []
    for command_cls in COMMANDS:
        get_command_data = globals().get(command_cls.Meta.key)
        data = extract_return_statement(get_command_data) if get_command_data else "{}"
        commands.append(CommandCode(**{"data": data, "class": command_cls}))

    write_protocol_code(cli_runner, plugin_path, commands)
    install_plugin(plugin_path, token)
    sleep(10)  # Wait for the plugin to be installed

    yield

    clean_up_files_and_plugins(plugin_path, token)


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


@pytest.fixture
def command_data(command_cls: type[_BaseCommand]) -> dict[str, Any]:
    """The command data to be used for command schema tests."""
    get_command_data = globals().get(command_cls.Meta.key)
    if not get_command_data:
        pytest.skip(f"No command values found for '{command_cls.Meta.key}'")

    return get_command_data()


@pytest.mark.integtest
def test_plugin_originates_command_in_note(
    token: MaskedValue,
    install_plugin_commands: None,
    note_for_originating_commands: dict,
    command_cls: type[_BaseCommand],
    command_data: dict[str, Any],
) -> None:
    """Test that commands with data are successfully originated in a note via plugin."""
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
    """Test that empty commands are successfully originated in a note via plugin."""
    if command_cls.Meta.key in EMPTY_COMMAND_NOT_ALLOWED:
        pytest.skip(
            f"Skipping '{command_cls.Meta.key}' due to command not being allowed to be inserted without values"
        )

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
    """Test that commands are successfully committed via plugin."""
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
