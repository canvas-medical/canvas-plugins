import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

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
from canvas_sdk.commands.tests.test_utils import (
    fake,
    get_field_type,
    raises_none_error_for_effect_method,
    raises_wrong_type_error,
)

runner = CliRunner()


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
        (PlanCommand, ("narrative", "command_uuid")),
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
    Command: type[_BaseCommand],
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
            {"narrative": "yo", "note_uuid": 1},
            "1 validation error for PlanCommand\nnote_uuid\n  Input should be a valid string [type=string_type",
            {"narrative": "yo", "note_uuid": "00000000-0000-0000-0000-000000000000"},
        ),
        (
            PlanCommand,
            {"narrative": "yo", "note_uuid": "5", "command_uuid": 5},
            "1 validation error for PlanCommand\ncommand_uuid\n  Input should be a valid string [type=string_type",
            {"narrative": "yo", "note_uuid": "5", "command_uuid": "5"},
        ),
        (
            ReasonForVisitCommand,
            {"note_uuid": "00000000-0000-0000-0000-000000000000", "structured": True},
            "1 validation error for ReasonForVisitCommand\n  Structured RFV should have a coding",
            {
                "note_uuid": "00000000-0000-0000-0000-000000000000",
                "structured": False,
            },
        ),
        (
            ReasonForVisitCommand,
            {
                "note_uuid": "00000000-0000-0000-0000-000000000000",
                "coding": {"code": "x"},
            },
            "1 validation error for ReasonForVisitCommand\ncoding.system\n  Field required [type=missing",
            {"note_uuid": "00000000-0000-0000-0000-000000000000"},
        ),
        (
            ReasonForVisitCommand,
            {
                "note_uuid": "00000000-0000-0000-0000-000000000000",
                "coding": {"code": 1, "system": "y"},
            },
            "1 validation error for ReasonForVisitCommand\ncoding.code\n  Input should be a valid string [type=string_type",
            {"note_uuid": "00000000-0000-0000-0000-000000000000"},
        ),
        (
            ReasonForVisitCommand,
            {
                "note_uuid": "00000000-0000-0000-0000-000000000000",
                "coding": {"code": None, "system": "y"},
            },
            "1 validation error for ReasonForVisitCommand\ncoding.code\n  Input should be a valid string [type=string_type",
            {"note_uuid": "00000000-0000-0000-0000-000000000000"},
        ),
        (
            ReasonForVisitCommand,
            {
                "note_uuid": "00000000-0000-0000-0000-000000000000",
                "coding": {"system": "y"},
            },
            "1 validation error for ReasonForVisitCommand\ncoding.code\n  Field required [type=missing",
            {"note_uuid": "00000000-0000-0000-0000-000000000000"},
        ),
        (
            ReasonForVisitCommand,
            {
                "note_uuid": "00000000-0000-0000-0000-000000000000",
                "coding": {"code": "x", "system": 1},
            },
            "1 validation error for ReasonForVisitCommand\ncoding.system\n  Input should be a valid string [type=string_type",
            {"note_uuid": "00000000-0000-0000-0000-000000000000"},
        ),
        (
            ReasonForVisitCommand,
            {
                "note_uuid": "00000000-0000-0000-0000-000000000000",
                "coding": {"code": "x", "system": None},
            },
            "1 validation error for ReasonForVisitCommand\ncoding.system\n  Input should be a valid string [type=string_type",
            {"note_uuid": "00000000-0000-0000-0000-000000000000"},
        ),
        (
            ReasonForVisitCommand,
            {
                "note_uuid": "00000000-0000-0000-0000-000000000000",
                "coding": {"code": "x", "system": "y", "display": 1},
            },
            "1 validation error for ReasonForVisitCommand\ncoding.display\n  Input should be a valid string [type=string_type",
            {"note_uuid": "00000000-0000-0000-0000-000000000000"},
        ),
    ],
)
def test_command_raises_specific_error_when_kwarg_given_incorrect_type(
    Command: type[PlanCommand] | type[ReasonForVisitCommand],
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
        (PlanCommand, ("narrative", "command_uuid", "note_uuid")),
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
    Command: type[_BaseCommand],
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
