from datetime import datetime

import pytest
import requests
from pydantic import ValidationError

import settings
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
from canvas_sdk.commands.constants import Coding
from canvas_sdk.commands.tests.test_utils import (
    fake,
    get_field_type,
    raises_missing_error,
    raises_none_error,
    raises_wrong_type_error,
)


@pytest.mark.parametrize(
    "Command,fields_to_test",
    [
        (AssessCommand, ("condition_id", "background", "status", "narrative")),
        (
            DiagnoseCommand,
            ("icd10_code", "background", "approximate_date_of_onset", "today_assessment"),
        ),
        (
            GoalCommand,
            (
                "goal_statement",
                "start_date",
                "due_date",
                "achievement_status",
                "priority",
                "progress",
            ),
        ),
        (HistoryOfPresentIllnessCommand, ("narrative",)),
        (MedicationStatementCommand, ("fdb_code", "sig")),
        (PlanCommand, ("narrative", "user_id", "command_uuid")),
        (
            PrescribeCommand,
            (
                "fdb_code",
                "icd10_codes",
                "sig",
                "days_supply",
                "quantity_to_dispense",
                "type_to_dispense",
                "refills",
                "substitutions",
                "pharmacy",
                "prescriber_id",
                "note_to_pharmacist",
            ),
        ),
        (QuestionnaireCommand, ("questionnaire_id", "result")),
        (ReasonForVisitCommand, ("coding", "comment")),
        (StopMedicationCommand, ("medication_id", "rationale")),
        (
            UpdateGoalCommand,
            (
                "goal_id",
                "due_date",
                "achievement_status",
                "priority",
                "progress",
            ),
        ),
    ],
)
def test_command_raises_generic_error_when_kwarg_given_incorrect_type(
    Command: (
        AssessCommand
        | DiagnoseCommand
        | GoalCommand
        | HistoryOfPresentIllnessCommand
        | MedicationStatementCommand
        | PlanCommand
        | PrescribeCommand
        | QuestionnaireCommand
        | ReasonForVisitCommand
        | StopMedicationCommand
        | UpdateGoalCommand
    ),
    fields_to_test: tuple[str],
) -> None:
    schema = Command.model_json_schema()
    schema["required"].append("note_id")
    required_fields = {k: v for k, v in schema["properties"].items() if k in schema["required"]}
    base = {field: fake(props, Command) for field, props in required_fields.items()}
    for field in fields_to_test:
        raises_wrong_type_error(base, Command, field)
        if field in required_fields:
            raises_missing_error(base, Command, field)
            raises_none_error(base, Command, field)


@pytest.mark.parametrize(
    "Command,err_kwargs,err_msg,valid_kwargs",
    [
        (
            PlanCommand,
            {"narrative": "yo", "user_id": 1},
            "1 validation error for PlanCommand\n  Value error, Command should have either a note_id or a command_uuid. [type=value",
            {"narrative": "yo", "note_id": 1, "user_id": 1},
        ),
        (
            PlanCommand,
            {"narrative": "yo", "user_id": 1, "note_id": None},
            "1 validation error for PlanCommand\n  Value error, Command should have either a note_id or a command_uuid. [type=value",
            {"narrative": "yo", "note_id": 1, "user_id": 1},
        ),
        (
            PlanCommand,
            {"narrative": "yo", "user_id": 5, "note_id": "100"},
            "1 validation error for PlanCommand\nnote_id\n  Input should be a valid integer [type=int_type",
            {"narrative": "yo", "note_id": 1, "user_id": 1},
        ),
        (
            ReasonForVisitCommand,
            {"note_id": 1, "user_id": 1, "structured": True},
            "1 validation error for ReasonForVisitCommand\n  Value error, Structured RFV should have a coding.",
            {"note_id": 1, "user_id": 1, "structured": False},
        ),
        (
            ReasonForVisitCommand,
            {"note_id": 1, "user_id": 1, "coding": {"code": "x"}},
            "1 validation error for ReasonForVisitCommand\ncoding.system\n  Field required [type=missing",
            {"note_id": 1, "user_id": 1},
        ),
        (
            ReasonForVisitCommand,
            {"note_id": 1, "user_id": 1, "coding": {"code": 1, "system": "y"}},
            "1 validation error for ReasonForVisitCommand\ncoding.code\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 1},
        ),
        (
            ReasonForVisitCommand,
            {"note_id": 1, "user_id": 1, "coding": {"code": None, "system": "y"}},
            "1 validation error for ReasonForVisitCommand\ncoding.code\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 1},
        ),
        (
            ReasonForVisitCommand,
            {"note_id": 1, "user_id": 1, "coding": {"system": "y"}},
            "1 validation error for ReasonForVisitCommand\ncoding.code\n  Field required [type=missing",
            {"note_id": 1, "user_id": 1},
        ),
        (
            ReasonForVisitCommand,
            {"note_id": 1, "user_id": 1, "coding": {"code": "x", "system": 1}},
            "1 validation error for ReasonForVisitCommand\ncoding.system\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 1},
        ),
        (
            ReasonForVisitCommand,
            {"note_id": 1, "user_id": 1, "coding": {"code": "x", "system": None}},
            "1 validation error for ReasonForVisitCommand\ncoding.system\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 1},
        ),
        (
            ReasonForVisitCommand,
            {"note_id": 1, "user_id": 1, "coding": {"code": "x", "system": "y", "display": 1}},
            "1 validation error for ReasonForVisitCommand\ncoding.display\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 1},
        ),
    ],
)
def test_command_raises_specific_error_when_kwarg_given_incorrect_type(
    Command: PlanCommand | ReasonForVisitCommand,
    err_kwargs: dict,
    err_msg: str,
    valid_kwargs: dict,
) -> None:
    with pytest.raises(ValidationError) as e1:
        Command(**err_kwargs)
    assert err_msg in repr(e1.value)

    cmd = Command(**valid_kwargs)
    if len(err_kwargs) < len(valid_kwargs):
        return
    key, value = list(err_kwargs.items())[-1]
    with pytest.raises(ValidationError) as e2:
        setattr(cmd, key, value)
    assert err_msg in repr(e2.value)


@pytest.mark.parametrize(
    "Command,fields_to_test",
    [
        (AssessCommand, ("condition_id", "background", "status", "narrative")),
        (
            DiagnoseCommand,
            ("icd10_code", "background", "approximate_date_of_onset", "today_assessment"),
        ),
        (
            GoalCommand,
            (
                "goal_statement",
                "start_date",
                "due_date",
                "achievement_status",
                "priority",
                "progress",
            ),
        ),
        (HistoryOfPresentIllnessCommand, ("narrative",)),
        (MedicationStatementCommand, ("fdb_code", "sig")),
        (PlanCommand, ("narrative", "user_id", "command_uuid", "note_id")),
        (
            PrescribeCommand,
            (
                "fdb_code",
                "icd10_codes",
                "sig",
                "days_supply",
                "quantity_to_dispense",
                "type_to_dispense",
                "refills",
                "substitutions",
                "pharmacy",
                "prescriber_id",
                "note_to_pharmacist",
            ),
        ),
        (QuestionnaireCommand, ("questionnaire_id", "result")),
        (ReasonForVisitCommand, ("coding", "comment")),
        (StopMedicationCommand, ("medication_id", "rationale")),
        (
            UpdateGoalCommand,
            (
                "goal_id",
                "due_date",
                "achievement_status",
                "priority",
                "progress",
            ),
        ),
    ],
)
def test_command_allows_kwarg_with_correct_type(
    Command: (
        AssessCommand
        | DiagnoseCommand
        | GoalCommand
        | HistoryOfPresentIllnessCommand
        | MedicationStatementCommand
        | PlanCommand
        | PrescribeCommand
        | QuestionnaireCommand
        | ReasonForVisitCommand
        | StopMedicationCommand
        | UpdateGoalCommand
    ),
    fields_to_test: tuple[str],
) -> None:
    schema = Command.model_json_schema()
    schema["required"].append("note_id")
    required_fields = {k: v for k, v in schema["properties"].items() if k in schema["required"]}
    base = {field: fake(props, Command) for field, props in required_fields.items()}

    for field in fields_to_test:
        field_type = get_field_type(Command.model_json_schema()["properties"][field])

        init_field_value = fake({"type": field_type}, Command)
        init_kwargs = base | {field: init_field_value}
        cmd = Command(**init_kwargs)
        assert getattr(cmd, field) == init_field_value

        updated_field_value = fake({"type": field_type}, Command)
        setattr(cmd, field, updated_field_value)
        assert getattr(cmd, field) == updated_field_value


@pytest.fixture(scope="session")
def token() -> str:
    return requests.post(
        f"{settings.INTEGRATION_TEST_URL}/auth/token/",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": settings.INTEGRATION_TEST_CLIENT_ID,
            "client_secret": settings.INTEGRATION_TEST_CLIENT_SECRET,
        },
    ).json()["access_token"]


@pytest.fixture
def note_id(token: str) -> str:
    headers = {
        "Authorization": f"Bearer {token}",
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
    note = requests.post(
        f"{settings.INTEGRATION_TEST_URL}/api/Note/", headers=headers, json=data
    ).json()
    return note["externallyExposableId"]


@pytest.fixture
def command_type_map() -> dict[str, type]:
    return {
        "AutocompleteField": str,
        "MultiLineTextField": str,
        "TextField": str,
        "ChoiceField": str,
        "DateField": datetime,
    }


@pytest.mark.integtest
@pytest.mark.parametrize(
    "Command",
    [
        (AssessCommand),
        # todo: add Diagnose once it has an adapter in home-app
        # (DiagnoseCommand),
        (GoalCommand),
        (HistoryOfPresentIllnessCommand),
        (MedicationStatementCommand),
        (PlanCommand),
        # todo: add Prescribe once its been refactored
        # (PrescribeCommand),
        (QuestionnaireCommand),
        (ReasonForVisitCommand),
        (StopMedicationCommand),
        (UpdateGoalCommand),
    ],
)
def test_command_schema_matches_command_api(
    token: str,
    command_type_map: dict[str, str],
    note_id: str,
    Command: (
        AssessCommand
        | DiagnoseCommand
        | GoalCommand
        | HistoryOfPresentIllnessCommand
        | MedicationStatementCommand
        | PlanCommand
        | PrescribeCommand
        | QuestionnaireCommand
        | ReasonForVisitCommand
        | StopMedicationCommand
        | UpdateGoalCommand
    ),
) -> None:
    # first create the command in the new note
    data = {"noteKey": note_id, "schemaKey": Command.Meta.key}
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{settings.INTEGRATION_TEST_URL}/core/api/v1/commands/"
    command_resp = requests.post(url, headers=headers, data=data).json()
    assert "uuid" in command_resp
    command_uuid = command_resp["uuid"]

    # next, request the fields of the newly created command
    url = f"{settings.INTEGRATION_TEST_URL}/core/api/v1/commands/{command_uuid}/fields/"
    command_fields_resp = requests.get(url, headers=headers).json()
    assert command_fields_resp["schema"] == Command.Meta.key

    command_fields = command_fields_resp["fields"]
    if Command.Meta.key == "questionnaire":
        # questionnaire's fields vary per questionnaire, so just check the first two fields which never vary
        command_fields = command_fields[:2]
    expected_fields = Command.command_schema()
    assert len(command_fields) == len(expected_fields)

    for actual_field in command_fields:
        name = actual_field["name"]
        assert name in expected_fields
        expected_field = expected_fields[name]

        assert expected_field["required"] == actual_field["required"]

        expected_type = expected_field["type"]
        if expected_type is Coding:
            expected_type = expected_type.__annotations__["code"]
        assert expected_type == command_type_map.get(actual_field["type"])

        if (choices := actual_field["choices"]) is None:
            assert expected_field["choices"] is None
            continue

        assert len(expected_field["choices"]) == len(choices)
        for choice in choices:
            assert choice["value"] in expected_field["choices"]
