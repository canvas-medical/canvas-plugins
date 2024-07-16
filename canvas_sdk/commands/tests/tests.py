import decimal
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
    MaskedValue,
    fake,
    get_field_type,
    raises_none_error_for_effect_method,
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
    for field in fields_to_test:
        raises_wrong_type_error(Command, field)

    for method in ["originate", "edit", "delete", "commit", "enter_in_error"]:
        raises_none_error_for_effect_method(Command, method)


@pytest.mark.parametrize(
    "Command,err_kwargs,err_msg,valid_kwargs",
    [
        (
            PlanCommand,
            {"narrative": "yo", "user_id": 5, "note_uuid": 1},
            "1 validation error for PlanCommand\nnote_uuid\n  Input should be a valid string [type=string_type",
            {"narrative": "yo", "note_uuid": "00000000-0000-0000-0000-000000000000", "user_id": 1},
        ),
        (
            PlanCommand,
            {"narrative": "yo", "user_id": 5, "note_uuid": "5", "command_uuid": 5},
            "1 validation error for PlanCommand\ncommand_uuid\n  Input should be a valid string [type=string_type",
            {"narrative": "yo", "user_id": 5, "note_uuid": "5", "command_uuid": "5"},
        ),
        (
            PlanCommand,
            {"narrative": "yo", "note_uuid": "5", "command_uuid": "4", "user_id": "5"},
            "1 validation error for PlanCommand\nuser_id\n  Input should be a valid integer [type=int_type",
            {"narrative": "yo", "note_uuid": "5", "command_uuid": "4", "user_id": 5},
        ),
        (
            ReasonForVisitCommand,
            {"note_uuid": "00000000-0000-0000-0000-000000000000", "user_id": 1, "structured": True},
            "1 validation error for ReasonForVisitCommand\n  Structured RFV should have a coding",
            {
                "note_uuid": "00000000-0000-0000-0000-000000000000",
                "user_id": 1,
                "structured": False,
            },
        ),
        (
            ReasonForVisitCommand,
            {
                "note_uuid": "00000000-0000-0000-0000-000000000000",
                "user_id": 1,
                "coding": {"code": "x"},
            },
            "1 validation error for ReasonForVisitCommand\ncoding.system\n  Field required [type=missing",
            {"note_uuid": "00000000-0000-0000-0000-000000000000", "user_id": 1},
        ),
        (
            ReasonForVisitCommand,
            {
                "note_uuid": "00000000-0000-0000-0000-000000000000",
                "user_id": 1,
                "coding": {"code": 1, "system": "y"},
            },
            "1 validation error for ReasonForVisitCommand\ncoding.code\n  Input should be a valid string [type=string_type",
            {"note_uuid": "00000000-0000-0000-0000-000000000000", "user_id": 1},
        ),
        (
            ReasonForVisitCommand,
            {
                "note_uuid": "00000000-0000-0000-0000-000000000000",
                "user_id": 1,
                "coding": {"code": None, "system": "y"},
            },
            "1 validation error for ReasonForVisitCommand\ncoding.code\n  Input should be a valid string [type=string_type",
            {"note_uuid": "00000000-0000-0000-0000-000000000000", "user_id": 1},
        ),
        (
            ReasonForVisitCommand,
            {
                "note_uuid": "00000000-0000-0000-0000-000000000000",
                "user_id": 1,
                "coding": {"system": "y"},
            },
            "1 validation error for ReasonForVisitCommand\ncoding.code\n  Field required [type=missing",
            {"note_uuid": "00000000-0000-0000-0000-000000000000", "user_id": 1},
        ),
        (
            ReasonForVisitCommand,
            {
                "note_uuid": "00000000-0000-0000-0000-000000000000",
                "user_id": 1,
                "coding": {"code": "x", "system": 1},
            },
            "1 validation error for ReasonForVisitCommand\ncoding.system\n  Input should be a valid string [type=string_type",
            {"note_uuid": "00000000-0000-0000-0000-000000000000", "user_id": 1},
        ),
        (
            ReasonForVisitCommand,
            {
                "note_uuid": "00000000-0000-0000-0000-000000000000",
                "user_id": 1,
                "coding": {"code": "x", "system": None},
            },
            "1 validation error for ReasonForVisitCommand\ncoding.system\n  Input should be a valid string [type=string_type",
            {"note_uuid": "00000000-0000-0000-0000-000000000000", "user_id": 1},
        ),
        (
            ReasonForVisitCommand,
            {
                "note_uuid": "00000000-0000-0000-0000-000000000000",
                "user_id": 1,
                "coding": {"code": "x", "system": "y", "display": 1},
            },
            "1 validation error for ReasonForVisitCommand\ncoding.display\n  Input should be a valid string [type=string_type",
            {"note_uuid": "00000000-0000-0000-0000-000000000000", "user_id": 1},
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
        cmd = Command(**err_kwargs)
        cmd.originate()
        cmd.edit()
    assert err_msg in repr(e1.value)

    cmd = Command(**valid_kwargs)
    if len(err_kwargs) < len(valid_kwargs):
        return
    key, value = list(err_kwargs.items())[-1]
    with pytest.raises(ValidationError) as e2:
        setattr(cmd, key, value)
        cmd.originate()
        cmd.edit()
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
        (PlanCommand, ("narrative", "user_id", "command_uuid", "note_uuid")),
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

    for field in fields_to_test:
        field_type = get_field_type(schema["properties"][field])

        init_field_value = fake({"type": field_type}, Command)
        init_kwargs = {field: init_field_value}
        cmd = Command(**init_kwargs)
        assert getattr(cmd, field) == init_field_value

        updated_field_value = fake({"type": field_type}, Command)
        setattr(cmd, field, updated_field_value)
        assert getattr(cmd, field) == updated_field_value

    for method in ["originate", "edit", "delete", "commit", "enter_in_error"]:
        required_fields = {
            k: v
            for k, v in schema["properties"].items()
            if k in Command()._get_effect_method_required_fields(method)
        }
        base = {field: fake(props, Command) for field, props in required_fields.items()}
        cmd = Command(**base)
        effect = getattr(cmd, method)()
        assert effect is not None


@pytest.fixture(scope="session")
def token() -> MaskedValue:
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


@pytest.fixture
def note_uuid(token: MaskedValue) -> str:
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
        "ApproximateDateField": datetime,
        "IntegerField": int,
        "DecimalField": decimal.Decimal,
    }


@pytest.mark.integtest
@pytest.mark.parametrize(
    "Command",
    [
        (AssessCommand),
        (DiagnoseCommand),
        (GoalCommand),
        (HistoryOfPresentIllnessCommand),
        (MedicationStatementCommand),
        (PlanCommand),
        (PrescribeCommand),
        (QuestionnaireCommand),
        (ReasonForVisitCommand),
        (StopMedicationCommand),
        (UpdateGoalCommand),
    ],
)
def test_command_schema_matches_command_api(
    token: MaskedValue,
    command_type_map: dict[str, str],
    note_uuid: str,
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
    data = {"noteKey": note_uuid, "schemaKey": Command.Meta.key}
    headers = {"Authorization": f"Bearer {token.value}"}
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

        actual_type = command_type_map.get(actual_field["type"])
        if actual_field["type"] == "AutocompleteField" and name[-1] == "s":
            # this condition initially created for Prescribe.indications,
            # but could apply to other AutocompleteField fields that are lists
            # making the assumption here that if the field ends in 's' (like indications), it is a list
            actual_type = list[actual_type]  # type: ignore

        assert expected_type == actual_type

        if (choices := actual_field["choices"]) is None:
            assert expected_field["choices"] is None
            continue

        assert len(expected_field["choices"]) == len(choices)
        for choice in choices:
            assert choice["value"] in expected_field["choices"]
