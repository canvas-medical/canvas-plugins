import json
from collections.abc import Generator
from datetime import date
from pathlib import Path
from time import sleep
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from pydantic_core import ValidationError
from typer.testing import CliRunner

from canvas_sdk.commands import (
    AllergyCommand,
    AssessCommand,
    ChartSectionReviewCommand,
    FamilyHistoryCommand,
    GoalCommand,
    InstructCommand,
    MedicationStatementCommand,
    PastSurgicalHistoryCommand,
    PerformCommand,
)
from canvas_sdk.commands.base import _BaseCommand
from canvas_sdk.commands.commands.allergy import Allergen, AllergenType
from canvas_sdk.commands.commands.immunization_statement import ImmunizationStatementCommand
from canvas_sdk.commands.commands.review.base import ReportReviewCommunicationMethod
from canvas_sdk.commands.constants import CodeSystems, Coding
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


def labReview() -> dict[str, Any]:
    """Lab Review Command for testing."""
    return {
        "message_to_patient": "Lab results reviewed",
        "communication_method": ReportReviewCommunicationMethod.ALREADY_REVIEWED_WITH_PATIENT,
        "comment": "Test lab review",
    }


def imagingReview() -> dict[str, Any]:
    """Imaging Review Command for testing."""
    return {
        "message_to_patient": "Imaging results reviewed",
        "communication_method": ReportReviewCommunicationMethod.ALREADY_REVIEWED_WITH_PATIENT,
        "comment": "Test imaging review",
    }


def referralReview() -> dict[str, Any]:
    """Referral Review Command for testing."""
    return {
        "message_to_patient": "Referral reviewed",
        "communication_method": ReportReviewCommunicationMethod.ALREADY_REVIEWED_WITH_PATIENT,
        "comment": "Test referral review",
    }


def uncategorizedDocumentReview() -> dict[str, Any]:
    """Uncategorized Document Review Command for testing."""
    return {
        "message_to_patient": "uncategorized document reviewed",
        "communication_method": ReportReviewCommunicationMethod.ALREADY_REVIEWED_WITH_PATIENT,
        "comment": "Test uncategorized clinical document review",
    }


def customCommand() -> dict[str, Any]:
    """CustomCommand for testing."""
    return {
        "content": "<h1>Hello world</h1>",
        "print_content": "<p>Hello world</p>",
    }


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
    plugin_dir = integration_tests_plugins_dir / "commands"
    package_name = plugin_dir.name.replace("-", "_")
    commands: list[CommandCode] = []
    for command_cls in COMMANDS:
        get_command_data = globals().get(command_cls.Meta.key)
        data = extract_return_statement(get_command_data) if get_command_data else "{}"
        commands.append(CommandCode(**{"data": data, "class": command_cls}))

    write_protocol_code(cli_runner, plugin_dir, commands)
    install_plugin(plugin_dir / package_name, token)
    sleep(10)  # Wait for the plugin to be installed

    yield

    clean_up_files_and_plugins(plugin_dir, token)


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


@pytest.mark.parametrize(
    "command_cls,field_name,valid_systems,invalid_system",
    [
        (
            MedicationStatementCommand,
            "fdb_code",
            [CodeSystems.FDB, CodeSystems.UNSTRUCTURED],
            CodeSystems.RXNORM,
        ),
        (
            PastSurgicalHistoryCommand,
            "past_surgical_history",
            [CodeSystems.SNOMED, CodeSystems.UNSTRUCTURED],
            CodeSystems.ICD10,
        ),
        (
            FamilyHistoryCommand,
            "family_history",
            [CodeSystems.SNOMED, CodeSystems.UNSTRUCTURED],
            CodeSystems.ICD10,
        ),
        (
            PerformCommand,
            "cpt_code",
            [CodeSystems.CPT, CodeSystems.UNSTRUCTURED],
            CodeSystems.HCPCS,
        ),
        (
            InstructCommand,
            "coding",
            [CodeSystems.SNOMED, CodeSystems.UNSTRUCTURED],
            CodeSystems.ICD10,
        ),
    ],
)
def test_coding_system_validation_with_valid_systems(
    command_cls: type[_BaseCommand],
    field_name: str,
    valid_systems: list[CodeSystems],
    invalid_system: CodeSystems,
) -> None:
    """Test that commands accept valid coding systems and reject invalid ones."""
    # Test valid systems
    for valid_system in valid_systems:
        coding = {"system": valid_system, "code": "test_code", "display": "Test Display"}
        command_data = {field_name: coding, "note_uuid": "test_uuid"}
        command = command_cls(**command_data).originate()
        parsed_coding = json.loads(command.payload)["data"][field_name]
        assert parsed_coding["system"] == valid_system

    # Test invalid system
    invalid_coding = {"system": invalid_system, "code": "test_code", "display": "Test Display"}
    command_data_invalid = {field_name: invalid_coding}

    with pytest.raises(ValidationError) as exc_info:
        command_cls(**command_data_invalid).originate()

    assert "coding.system" in str(exc_info.value).lower()


@pytest.mark.parametrize(
    "command_cls,field_name,value",
    [
        (MedicationStatementCommand, "fdb_code", "123456"),
        (PastSurgicalHistoryCommand, "past_surgical_history", "condition"),
        (FamilyHistoryCommand, "family_history", "condition"),
        (PerformCommand, "cpt_code", "789456"),
    ],
)
def test_coding_system_validation_accepts_string_values(
    command_cls: type[_BaseCommand],
    field_name: str,
    value: str,
) -> None:
    """Test that commands accept string values for coding systems without errors."""
    command_data = {field_name: value, "note_uuid": "test_uuid"}
    command = command_cls(**command_data).originate()
    parsed_value = json.loads(command.payload)["data"][field_name]
    assert parsed_value == value


def test_immunization_statement_values_are_set_correctly() -> None:
    """Test that ImmunizationStatementCommand sets values correctly."""
    # Test with CPT and CVX codes
    cpt_coding = Coding(
        system=CodeSystems.CPT,
        code="90471",
        display="Immunization administration",
    )
    cvx_coding = Coding(system=CodeSystems.CVX, code="207", display="COVID-19 vaccine")
    approximate_date_value = date(2024, 1, 15)
    comments_value = "Patient tolerated well"

    command = ImmunizationStatementCommand(
        note_uuid="test_uuid",
        cpt_code=cpt_coding,
        cvx_code=cvx_coding,
        approximate_date=approximate_date_value,
        comments=comments_value,
    ).originate()

    payload = json.loads(command.payload)
    data = payload["data"]

    assert data["cpt_code"]["system"] == CodeSystems.CPT
    assert data["cpt_code"]["code"] == "90471"
    assert data["cpt_code"]["display"] == "Immunization administration"

    assert data["cvx_code"]["system"] == CodeSystems.CVX
    assert data["cvx_code"]["code"] == "207"
    assert data["cvx_code"]["display"] == "COVID-19 vaccine"

    assert data["approximate_date"] == "2024-01-15"
    assert data["comments"] == comments_value

    # Test with values after instantiation
    immunization_statement_command = ImmunizationStatementCommand(
        note_uuid="test_uuid",
        approximate_date=approximate_date_value,
        comments=comments_value,
    )
    immunization_statement_command.cpt_code = cpt_coding
    immunization_statement_command.cvx_code = cvx_coding

    command = immunization_statement_command.originate()

    payload = json.loads(command.payload)
    data = payload["data"]

    assert data["cpt_code"]["system"] == CodeSystems.CPT
    assert data["cpt_code"]["code"] == "90471"
    assert data["cpt_code"]["display"] == "Immunization administration"

    assert data["cvx_code"]["system"] == CodeSystems.CVX
    assert data["cvx_code"]["code"] == "207"
    assert data["cvx_code"]["display"] == "COVID-19 vaccine"

    assert data["approximate_date"] == "2024-01-15"
    assert data["comments"] == comments_value

    # Test with unstructured code
    unstructured_coding = Coding(
        system=CodeSystems.UNSTRUCTURED,
        code="flu shot",
        display="Flu shot",
    )

    command = ImmunizationStatementCommand(
        note_uuid="test_uuid",
        unstructured=unstructured_coding,
        approximate_date=approximate_date_value,
        comments=comments_value,
    ).originate()

    payload = json.loads(command.payload)
    data = payload["data"]

    assert data["unstructured"]["system"] == CodeSystems.UNSTRUCTURED
    assert data["unstructured"]["code"] == "flu shot"
    assert data["unstructured"]["display"] == "Flu shot"
    assert data["approximate_date"] == "2024-01-15"
    assert data["comments"] == comments_value

    # Test with value set after instantiation
    immunization_statement_command = ImmunizationStatementCommand(
        note_uuid="test_uuid",
        approximate_date=approximate_date_value,
        comments=comments_value,
    )
    immunization_statement_command.unstructured = unstructured_coding
    command = immunization_statement_command.originate()

    payload = json.loads(command.payload)
    data = payload["data"]

    assert data["unstructured"]["system"] == CodeSystems.UNSTRUCTURED
    assert data["unstructured"]["code"] == "flu shot"
    assert data["unstructured"]["display"] == "Flu shot"
    assert data["approximate_date"] == "2024-01-15"
    assert data["comments"] == comments_value


def test_immunization_statement_cpt_and_cvx_required_together() -> None:
    """Test that CPT and CVX codes must be provided together."""
    cpt_coding = Coding(
        system=CodeSystems.CPT,
        code="90471",
        display="Immunization administration",
    )
    cvx_coding = Coding(system=CodeSystems.CVX, code="207", display="COVID-19 vaccine")

    # Test CPT without CVX raises error
    with pytest.raises(ValidationError) as exc_info:
        ImmunizationStatementCommand(
            note_uuid="test_uuid",
            cpt_code=cpt_coding,
        ).originate()
    assert (
        "Both cpt_code and cvx_code must be provided if one is specified and cannot be empty"
        in str(exc_info.value)
    )

    # Test CVX without CPT raises error
    with pytest.raises(ValidationError) as exc_info:
        ImmunizationStatementCommand(
            note_uuid="test_uuid",
            cvx_code=cvx_coding,
        ).originate()
    assert (
        "Both cpt_code and cvx_code must be provided if one is specified and cannot be empty"
        in str(exc_info.value)
    )


def test_immunization_statement_unstructured_cannot_be_used_with_cpt_or_cvx() -> None:
    """Test that unstructured codes cannot be used together with CPT or CVX codes."""
    cpt_coding = Coding(
        system=CodeSystems.CPT,
        code="90471",
        display="Immunization administration",
    )
    cvx_coding = Coding(system=CodeSystems.CVX, code="207", display="COVID-19 vaccine")
    unstructured_coding = Coding(
        system=CodeSystems.UNSTRUCTURED,
        code="flu shot",
        display="Flu shot",
    )

    # Test unstructured with CPT and CVX raises error
    with pytest.raises(ValidationError) as exc_info:
        ImmunizationStatementCommand(
            note_uuid="test_uuid",
            cpt_code=cpt_coding,
            cvx_code=cvx_coding,
            unstructured=unstructured_coding,
        ).originate()
    assert "Unstructured codes cannot be used with CPT or CVX codes" in str(exc_info.value)


def test_immunization_statement_can_be_originated_without_values() -> None:
    """Test that ImmunizationStatementCommand can be originated without any values."""
    command = ImmunizationStatementCommand(note_uuid="test_uuid").originate()

    payload = json.loads(command.payload)
    data = payload["data"]

    # Verify that the command can be created and originated
    assert payload["note"] == "test_uuid"
    assert data.get("cpt_code") is None
    assert data.get("cvx_code") is None
    assert data.get("unstructured") is None
    assert data.get("approximate_date") is None
    assert data.get("comments") is None


def test_immunization_statement_empty_coding_raises_error() -> None:
    """Test that an empty Coding object raises a validation error due to missing required fields."""
    # Test empty dict for cpt_code
    with pytest.raises(ValidationError) as exc_info:
        ImmunizationStatementCommand(
            note_uuid="test_uuid",
            cpt_code={},  # type:ignore [arg-type]
            cvx_code=Coding(system=CodeSystems.CVX, code="207"),
        )
    assert "cpt_code" in str(exc_info.value).lower()

    # Test empty dict for cvx_code
    with pytest.raises(ValidationError) as exc_info:
        ImmunizationStatementCommand(
            note_uuid="test_uuid",
            cpt_code=Coding(system=CodeSystems.CPT, code="90471"),
            cvx_code={},  # type:ignore [arg-type]
        )
    assert "cvx_code" in str(exc_info.value).lower()

    # Test empty dict for unstructured
    with pytest.raises(ValidationError) as exc_info:
        ImmunizationStatementCommand(
            note_uuid="test_uuid",
            unstructured={},  # type:ignore [arg-type]
        )
    assert "unstructured" in str(exc_info.value).lower()

    # Test Coding with missing 'code' field
    with pytest.raises(ValidationError) as exc_info:
        ImmunizationStatementCommand(
            note_uuid="test_uuid",
            cpt_code={"system": CodeSystems.CPT},  # type:ignore [arg-type]
            cvx_code=Coding(system=CodeSystems.CVX, code="207"),
        )
    assert "code" in str(exc_info.value).lower()

    # Test Coding with missing 'system' field
    with pytest.raises(ValidationError) as exc_info:
        ImmunizationStatementCommand(
            note_uuid="test_uuid",
            unstructured={"code": "some immunization"},  # type:ignore [arg-type]
        )
    assert "system" in str(exc_info.value).lower()
