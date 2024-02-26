from datetime import datetime

import pytest
from pydantic import ValidationError

from canvas_sdk.commands import (
    AssessCommand,
    DiagnoseCommand,
    GoalCommand,
    HistoryOfPresentIllnessCommand,
    MedicationStatementCommand,
    PlanCommand,
    QuestionnaireCommand,
    ReasonForVisitCommand,
    StopMedicationCommand,
)


@pytest.mark.parametrize(
    "Command,err_kwargs,err_msg,valid_kwargs",
    [
        (
            PlanCommand,
            {"user_id": 1},
            "1 validation error for PlanCommand\n  Value error, Command should have either a note_id or a command_uuid. [type=value",
            {"note_id": 1, "user_id": 1},
        ),
        (
            PlanCommand,
            {"note_id": 1},
            "1 validation error for PlanCommand\nuser_id\n  Field required [type=missing",
            {"note_id": 1, "user_id": 1},
        ),
        (
            PlanCommand,
            {"note_id": 1, "user_id": None},
            "1 validation error for PlanCommand\nuser_id\n  Input should be a valid integer [type=int_type",
            {"note_id": 1, "user_id": 1},
        ),
        (
            PlanCommand,
            {"note_id": 1, "user_id": "5"},
            "1 validation error for PlanCommand\nuser_id\n  Input should be a valid integer [type=int_type",
            {"note_id": 1, "user_id": 1},
        ),
        (
            PlanCommand,
            {"user_id": 5, "note_id": "100"},
            "1 validation error for PlanCommand\nnote_id\n  Input should be a valid integer [type=int_type",
            {"note_id": 1, "user_id": 1},
        ),
        (
            PlanCommand,
            {"note_id": 1, "user_id": 5, "command_uuid": 100},
            "1 validation error for PlanCommand\ncommand_uuid\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 1},
        ),
        (
            PlanCommand,
            {"note_id": 1, "user_id": 5, "narrative": 143},
            "1 validation error for PlanCommand\nnarrative\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 1},
        ),
        (
            AssessCommand,
            {"note_id": 1, "user_id": 5},
            "1 validation error for AssessCommand\ncondition_id\n  Field required [type=missing",
            {"note_id": 1, "user_id": 1, "condition_id": 100},
        ),
        (
            AssessCommand,
            {"note_id": 1, "user_id": 5, "condition_id": None},
            "1 validation error for AssessCommand\ncondition_id\n  Input should be a valid integer [type=int_type",
            {"note_id": 1, "user_id": 1, "condition_id": 100},
        ),
        (
            AssessCommand,
            {"note_id": 1, "user_id": 5, "condition_id": "h"},
            "1 validation error for AssessCommand\ncondition_id\n  Input should be a valid integer [type=int_type",
            {"note_id": 1, "user_id": 1, "condition_id": 100},
        ),
        (
            AssessCommand,
            {"note_id": 1, "user_id": 5, "condition_id": 100, "background": 100},
            "1 validation error for AssessCommand\nbackground\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 1, "condition_id": 100},
        ),
        (
            AssessCommand,
            {"note_id": 1, "user_id": 5, "condition_id": 100, "status": "active"},
            "1 validation error for AssessCommand\nstatus\n  Input should be an instance of AssessCommand.Status [type=is_instance_of",
            {"note_id": 1, "user_id": 1, "condition_id": 100},
        ),
        (
            AssessCommand,
            {"note_id": 1, "user_id": 5, "condition_id": 100, "narrative": 1},
            "1 validation error for AssessCommand\nnarrative\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 1, "condition_id": 100},
        ),
        (
            DiagnoseCommand,
            {"note_id": 1, "user_id": 5},
            "1 validation error for DiagnoseCommand\nicd10_code\n  Field required [type=missing",
            {"note_id": 1, "user_id": 1, "icd10_code": "Z00"},
        ),
        (
            DiagnoseCommand,
            {"note_id": 1, "user_id": 5, "icd10_code": None},
            "1 validation error for DiagnoseCommand\nicd10_code\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 1, "icd10_code": "Z00"},
        ),
        (
            DiagnoseCommand,
            {"note_id": 1, "user_id": 5, "icd10_code": 1},
            "1 validation error for DiagnoseCommand\nicd10_code\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 1, "icd10_code": "Z00"},
        ),
        (
            DiagnoseCommand,
            {"note_id": 1, "user_id": 5, "icd10_code": "Z00", "background": 1},
            "1 validation error for DiagnoseCommand\nbackground\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 1, "icd10_code": "Z00"},
        ),
        (
            DiagnoseCommand,
            {"note_id": 1, "user_id": 5, "icd10_code": "Z00", "approximate_date_of_onset": 1},
            "1 validation error for DiagnoseCommand\napproximate_date_of_onset\n  Input should be a valid datetime [type=datetime_type",
            {"note_id": 1, "user_id": 1, "icd10_code": "Z00"},
        ),
        (
            DiagnoseCommand,
            {"note_id": 1, "user_id": 5, "icd10_code": "Z00", "approximate_date_of_onset": "1"},
            "1 validation error for DiagnoseCommand\napproximate_date_of_onset\n  Input should be a valid datetime [type=datetime_type",
            {"note_id": 1, "user_id": 1, "icd10_code": "Z00"},
        ),
        (
            DiagnoseCommand,
            {"note_id": 1, "user_id": 5, "icd10_code": "Z00", "today_assessment": 1},
            "1 validation error for DiagnoseCommand\ntoday_assessment\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 1, "icd10_code": "Z00"},
        ),
        (
            GoalCommand,
            {"note_id": 1, "user_id": 5},
            "1 validation error for GoalCommand\ngoal_statement\n  Field required [type=missing",
            {"note_id": 1, "user_id": 5, "goal_statement": "do some stuff!"},
        ),
        (
            GoalCommand,
            {"note_id": 1, "user_id": 5, "goal_statement": None},
            "1 validation error for GoalCommand\ngoal_statement\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 5, "goal_statement": "do some stuff!"},
        ),
        (
            GoalCommand,
            {"note_id": 1, "user_id": 5, "goal_statement": 1},
            "1 validation error for GoalCommand\ngoal_statement\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 5, "goal_statement": "do some stuff!"},
        ),
        (
            GoalCommand,
            {"note_id": 1, "user_id": 5, "goal_statement": "do some stuff!", "start_date": 1},
            "1 validation error for GoalCommand\nstart_date\n  Input should be a valid datetime [type=datetime_type",
            {"note_id": 1, "user_id": 1, "goal_statement": "do some stuff!"},
        ),
        (
            GoalCommand,
            {"note_id": 1, "user_id": 5, "goal_statement": "do some stuff!", "start_date": "1"},
            "1 validation error for GoalCommand\nstart_date\n  Input should be a valid datetime [type=datetime_type",
            {"note_id": 1, "user_id": 1, "goal_statement": "do some stuff!"},
        ),
        (
            GoalCommand,
            {"note_id": 1, "user_id": 5, "goal_statement": "do some stuff!", "due_date": 1},
            "1 validation error for GoalCommand\ndue_date\n  Input should be a valid datetime [type=datetime_type",
            {"note_id": 1, "user_id": 1, "goal_statement": "do some stuff!"},
        ),
        (
            GoalCommand,
            {"note_id": 1, "user_id": 5, "goal_statement": "do some stuff!", "due_date": "1"},
            "1 validation error for GoalCommand\ndue_date\n  Input should be a valid datetime [type=datetime_type",
            {"note_id": 1, "user_id": 1, "goal_statement": "do some stuff!"},
        ),
        (
            GoalCommand,
            {"note_id": 1, "user_id": 5, "goal_statement": "do some stuff!", "today_assessment": 1},
            "1 validation error for GoalCommand\ntoday_assessment\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 1, "goal_statement": "do some stuff!"},
        ),
        (
            GoalCommand,
            {
                "note_id": 1,
                "user_id": 5,
                "goal_statement": "do some stuff!",
                "achievement_status": "improving",
            },
            "1 validation error for GoalCommand\nachievement_status\n  Input should be an instance of GoalCommand.AchievementStatus [type=is_instance_of",
            {"note_id": 1, "user_id": 1, "goal_statement": "do some stuff!"},
        ),
        (
            GoalCommand,
            {
                "note_id": 1,
                "user_id": 5,
                "goal_statement": "do some stuff!",
                "priority": "medium-priority",
            },
            "1 validation error for GoalCommand\npriority\n  Input should be an instance of GoalCommand.Priority [type=is_instance_of",
            {"note_id": 1, "user_id": 1, "goal_statement": "do some stuff!"},
        ),
        (
            GoalCommand,
            {"note_id": 1, "user_id": 5, "goal_statement": "do some stuff!", "progress": 1},
            "1 validation error for GoalCommand\nprogress\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 5, "goal_statement": "do some stuff!"},
        ),
        (
            HistoryOfPresentIllnessCommand,
            {"note_id": 1, "user_id": 5},
            "1 validation error for HistoryOfPresentIllnessCommand\nnarrative\n  Field required [type=missing",
            {"note_id": 1, "user_id": 1, "narrative": "hiya"},
        ),
        (
            HistoryOfPresentIllnessCommand,
            {"note_id": 1, "user_id": 5, "narrative": None},
            "1 validation error for HistoryOfPresentIllnessCommand\nnarrative\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 1, "narrative": "hiya"},
        ),
        (
            MedicationStatementCommand,
            {"note_id": 1, "user_id": 1},
            "1 validation error for MedicationStatementCommand\nfdb_code\n  Field required [type=missing",
            {"note_id": 1, "user_id": 1, "fdb_code": "44"},
        ),
        (
            MedicationStatementCommand,
            {"note_id": 1, "user_id": 1, "fdb_code": None},
            "1 validation error for MedicationStatementCommand\nfdb_code\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 1, "fdb_code": "44"},
        ),
        (
            MedicationStatementCommand,
            {"note_id": 1, "user_id": 1, "fdb_code": "44", "sig": 1},
            "1 validation error for MedicationStatementCommand\nsig\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 1, "fdb_code": "44"},
        ),
        (
            QuestionnaireCommand,
            {"note_id": 1, "user_id": 1},
            "1 validation error for QuestionnaireCommand\nquestionnaire_id\n  Field required [type=missing",
            {"note_id": 1, "user_id": 1, "questionnaire_id": 500},
        ),
        (
            QuestionnaireCommand,
            {"note_id": 1, "user_id": 1, "questionnaire_id": None},
            "1 validation error for QuestionnaireCommand\nquestionnaire_id\n  Input should be a valid integer [type=int_type",
            {"note_id": 1, "user_id": 1, "questionnaire_id": 500},
        ),
        (
            QuestionnaireCommand,
            {"note_id": 1, "user_id": 1, "questionnaire_id": "5"},
            "1 validation error for QuestionnaireCommand\nquestionnaire_id\n  Input should be a valid integer [type=int_type",
            {"note_id": 1, "user_id": 1, "questionnaire_id": 500},
        ),
        (
            QuestionnaireCommand,
            {"note_id": 1, "user_id": 1, "questionnaire_id": 5, "result": 5},
            "1 validation error for QuestionnaireCommand\nresult\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 1, "questionnaire_id": 5},
        ),
        (
            ReasonForVisitCommand,
            {"note_id": 1, "user_id": 1, "structured": True},
            "1 validation error for ReasonForVisitCommand\n  Value error, Structured RFV should have a coding.",
            {"note_id": 1, "user_id": 1, "structured": False},
        ),
        (
            ReasonForVisitCommand,
            {"note_id": 1, "user_id": 1, "coding": "h"},
            "1 validation error for ReasonForVisitCommand\ncoding\n  Input should be a valid dictionary [type=dict_type",
            {"note_id": 1, "user_id": 1},
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
        (
            ReasonForVisitCommand,
            {"note_id": 1, "user_id": 1, "comment": 5},
            "1 validation error for ReasonForVisitCommand\ncomment\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 1},
        ),
        (
            StopMedicationCommand,
            {"note_id": 1, "user_id": 1},
            "1 validation error for StopMedicationCommand\nmedication_id\n  Field required [type=missing",
            {"note_id": 1, "user_id": 1, "medication_id": 500},
        ),
        (
            StopMedicationCommand,
            {"note_id": 1, "user_id": 1, "medication_id": None},
            "1 validation error for StopMedicationCommand\nmedication_id\n  Input should be a valid integer [type=int_type",
            {"note_id": 1, "user_id": 1, "medication_id": 500},
        ),
        (
            StopMedicationCommand,
            {"note_id": 1, "user_id": 1, "medication_id": "5"},
            "1 validation error for StopMedicationCommand\nmedication_id\n  Input should be a valid integer [type=int_type",
            {"note_id": 1, "user_id": 1, "medication_id": 500},
        ),
        (
            StopMedicationCommand,
            {"note_id": 1, "user_id": 1, "medication_id": 5, "rationale": 5},
            "1 validation error for StopMedicationCommand\nrationale\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 1, "medication_id": 5},
        ),
    ],
)
def test_command_raises_error_when_kwarg_given_incorrect_type(
    Command: (
        PlanCommand
        | AssessCommand
        | DiagnoseCommand
        | GoalCommand
        | HistoryOfPresentIllnessCommand
        | MedicationStatementCommand
        | QuestionnaireCommand
        | ReasonForVisitCommand
        | StopMedicationCommand
    ),
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
    "Command, test_init_kwarg,test_updated_value",
    [
        (PlanCommand, {"note_id": 1, "user_id": 100}, {"note_id": 1, "user_id": 7}),
        (
            PlanCommand,
            {"command_uuid": "1", "user_id": 100, "note_id": 200},
            {"command_uuid": "1", "user_id": 100, "note_id": None},
        ),
        (
            PlanCommand,
            {"note_id": 1, "user_id": 100, "command_uuid": "800"},
            {"note_id": 1, "user_id": 100, "command_uuid": None},
        ),
        (
            PlanCommand,
            {"note_id": 1, "user_id": 100, "narrative": "123456"},
            {"note_id": 1, "user_id": 100, "narrative": None},
        ),
        (
            AssessCommand,
            {"note_id": 1, "user_id": 100, "condition_id": 100},
            {"note_id": 1, "user_id": 100, "condition_id": 9},
        ),
        (
            AssessCommand,
            {"note_id": 1, "user_id": 100, "condition_id": 100, "background": "abcdefg"},
            {"note_id": 1, "user_id": 100, "condition_id": 100, "background": None},
        ),
        (
            AssessCommand,
            {
                "note_id": 1,
                "user_id": 100,
                "condition_id": 100,
                "status": AssessCommand.Status.DETERIORATED,
            },
            {"note_id": 1, "user_id": 100, "condition_id": 100, "status": None},
        ),
        (
            AssessCommand,
            {"note_id": 1, "user_id": 100, "condition_id": 100, "narrative": "1234567"},
            {"note_id": 1, "user_id": 100, "condition_id": 100, "narrative": None},
        ),
        (
            DiagnoseCommand,
            {"note_id": 1, "user_id": 1, "icd10_code": "Z00"},
            {"note_id": 1, "user_id": 1, "icd10_code": "400"},
        ),
        (
            DiagnoseCommand,
            {"note_id": 1, "user_id": 1, "icd10_code": "Z00", "background": "123"},
            {"note_id": 1, "user_id": 1, "icd10_code": "Z00", "background": None},
        ),
        (
            DiagnoseCommand,
            {
                "note_id": 1,
                "user_id": 1,
                "icd10_code": "Z00",
                "approximate_date_of_onset": datetime.now(),
            },
            {"note_id": 1, "user_id": 1, "icd10_code": "Z00", "approximate_date_of_onset": None},
        ),
        (
            DiagnoseCommand,
            {"note_id": 1, "user_id": 1, "icd10_code": "Z00", "today_assessment": "hi"},
            {"note_id": 1, "user_id": 1, "icd10_code": "Z00", "today_assessment": None},
        ),
        (
            GoalCommand,
            {"note_id": 1, "user_id": 1, "goal_statement": "get out there!"},
            {"note_id": 1, "user_id": 1, "goal_statement": "do some stuff!"},
        ),
        (
            GoalCommand,
            {
                "note_id": 1,
                "user_id": 1,
                "goal_statement": "get out there!",
                "start_date": datetime.now(),
            },
            {"note_id": 1, "user_id": 1, "goal_statement": "get out there!", "start_date": None},
        ),
        (
            GoalCommand,
            {
                "note_id": 1,
                "user_id": 1,
                "goal_statement": "get out there!",
                "due_date": datetime.now(),
            },
            {"note_id": 1, "user_id": 1, "goal_statement": "get out there!", "due_date": None},
        ),
        (
            GoalCommand,
            {
                "note_id": 1,
                "user_id": 1,
                "goal_statement": "get out there!",
                "today_assessment": "wee-ooo",
            },
            {
                "note_id": 1,
                "user_id": 1,
                "goal_statement": "get out there!",
                "today_assessment": None,
            },
        ),
        (
            GoalCommand,
            {
                "note_id": 1,
                "user_id": 100,
                "goal_statement": "get out there!",
                "achievement_status": GoalCommand.AchievementStatus.IN_PROGRESS,
            },
            {
                "note_id": 1,
                "user_id": 100,
                "goal_statement": "get out there!",
                "achievement_status": None,
            },
        ),
        (
            GoalCommand,
            {
                "note_id": 1,
                "user_id": 100,
                "goal_statement": "get out there!",
                "priority": GoalCommand.Priority.MEDIUM,
            },
            {"note_id": 1, "user_id": 100, "goal_statement": "get out there!", "priority": None},
        ),
        (
            GoalCommand,
            {"note_id": 1, "user_id": 1, "goal_statement": "get out there!", "progress": "hi"},
            {"note_id": 1, "user_id": 1, "goal_statement": "get out there!", "progress": None},
        ),
        (
            HistoryOfPresentIllnessCommand,
            {"note_id": 1, "user_id": 1, "narrative": "hi!"},
            {"note_id": 1, "user_id": 1, "narrative": "hows your day!"},
        ),
        (
            MedicationStatementCommand,
            {"note_id": 1, "user_id": 1, "fdb_code": "9888"},
            {"note_id": 1, "user_id": 1, "fdb_code": "12333"},
        ),
        (
            MedicationStatementCommand,
            {"note_id": 1, "user_id": 1, "fdb_code": "9888", "sig": "1pobd"},
            {"note_id": 1, "user_id": 1, "fdb_code": "9888", "sig": None},
        ),
        (
            QuestionnaireCommand,
            {"note_id": 1, "user_id": 1, "questionnaire_id": 10},
            {"note_id": 1, "user_id": 1, "questionnaire_id": 1000},
        ),
        (
            QuestionnaireCommand,
            {"note_id": 1, "user_id": 1, "questionnaire_id": 10, "result": "hi"},
            {"note_id": 1, "user_id": 1, "questionnaire_id": 10, "result": None},
        ),
        (
            ReasonForVisitCommand,
            {
                "note_id": 1,
                "user_id": 1,
                "structured": True,
                "coding": {"code": "x", "system": "y"},
            },
            {
                "note_id": 1,
                "user_id": 1,
                "structured": True,
                "coding": {"code": "xx", "system": "yy"},
            },
        ),
        (
            ReasonForVisitCommand,
            {
                "note_id": 1,
                "user_id": 1,
                "coding": {"code": "x", "system": "y"},
                "structured": True,
            },
            {
                "note_id": 1,
                "user_id": 1,
                "coding": {"code": "x", "system": "y"},
                "structured": False,
            },
        ),
        (
            ReasonForVisitCommand,
            {"note_id": 1, "user_id": 1, "structured": False, "coding": None},
            {
                "note_id": 1,
                "user_id": 1,
                "structured": False,
                "coding": {"code": "x", "system": "y"},
            },
        ),
        (
            ReasonForVisitCommand,
            {"note_id": 1, "user_id": 1, "comment": "hey"},
            {"note_id": 1, "user_id": 1, "comment": None},
        ),
        (
            StopMedicationCommand,
            {"note_id": 1, "user_id": 1, "medication_id": 10},
            {"note_id": 1, "user_id": 1, "medication_id": 1000},
        ),
        (
            StopMedicationCommand,
            {"note_id": 1, "user_id": 1, "medication_id": 10, "rationale": "hi"},
            {"note_id": 1, "user_id": 1, "medication_id": 10, "rationale": None},
        ),
    ],
)
def test_command_allows_kwarg_with_correct_type(
    Command: (
        PlanCommand
        | AssessCommand
        | DiagnoseCommand
        | GoalCommand
        | HistoryOfPresentIllnessCommand
        | MedicationStatementCommand
        | QuestionnaireCommand
        | ReasonForVisitCommand
        | StopMedicationCommand
    ),
    test_init_kwarg: dict,
    test_updated_value: dict,
) -> None:
    cmd = Command(**test_init_kwarg)

    init_k, init_v = list(test_init_kwarg.items())[-1]
    assert getattr(cmd, init_k) == init_v

    updated_k, updated_v = list(test_updated_value.items())[-1]
    setattr(cmd, updated_k, updated_v)
    assert getattr(cmd, updated_k) == updated_v
