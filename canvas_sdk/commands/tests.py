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
    QuestionnaireCommand,
    ReasonForVisitCommand,
    StopMedicationCommand,
)
from canvas_sdk.commands.constants import Coding


@pytest.mark.parametrize(
    "Command,err_kwargs,err_msg,valid_kwargs",
    [
        (
            AssessCommand,
            {"note_id": 1, "user_id": 5},
            "1 validation error for AssessCommand\ncondition_id\n  Field required [type=missing",
            {"note_id": 1, "user_id": 1, "condition_id": "100"},
        ),
        (
            AssessCommand,
            {"note_id": 1, "user_id": 5, "condition_id": None},
            "1 validation error for AssessCommand\ncondition_id\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 1, "condition_id": "100"},
        ),
        (
            AssessCommand,
            {"note_id": 1, "user_id": 5, "condition_id": 1},
            "1 validation error for AssessCommand\ncondition_id\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 1, "condition_id": "100"},
        ),
        (
            AssessCommand,
            {"note_id": 1, "user_id": 5, "condition_id": "100", "background": 100},
            "1 validation error for AssessCommand\nbackground\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 1, "condition_id": "100"},
        ),
        (
            AssessCommand,
            {"note_id": 1, "user_id": 5, "condition_id": "100", "status": "active"},
            "1 validation error for AssessCommand\nstatus\n  Input should be an instance of AssessCommand.Status [type=is_instance_of",
            {"note_id": 1, "user_id": 1, "condition_id": "100"},
        ),
        (
            AssessCommand,
            {"note_id": 1, "user_id": 5, "condition_id": "100", "narrative": 1},
            "1 validation error for AssessCommand\nnarrative\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 1, "condition_id": "100"},
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
            PlanCommand,
            {"narrative": "yo", "user_id": 1},
            "1 validation error for PlanCommand\n  Value error, Command should have either a note_id or a command_uuid. [type=value",
            {"narrative": "yo", "note_id": 1, "user_id": 1},
        ),
        (
            PlanCommand,
            {"narrative": "yo", "note_id": 1},
            "1 validation error for PlanCommand\nuser_id\n  Field required [type=missing",
            {"narrative": "yo", "note_id": 1, "user_id": 1},
        ),
        (
            PlanCommand,
            {"narrative": "yo", "note_id": 1, "user_id": None},
            "1 validation error for PlanCommand\nuser_id\n  Input should be a valid integer [type=int_type",
            {"narrative": "yo", "note_id": 1, "user_id": 1},
        ),
        (
            PlanCommand,
            {"narrative": "yo", "note_id": 1, "user_id": "5"},
            "1 validation error for PlanCommand\nuser_id\n  Input should be a valid integer [type=int_type",
            {"narrative": "yo", "note_id": 1, "user_id": 1},
        ),
        (
            PlanCommand,
            {"narrative": "yo", "user_id": 5, "note_id": "100"},
            "1 validation error for PlanCommand\nnote_id\n  Input should be a valid integer [type=int_type",
            {"narrative": "yo", "note_id": 1, "user_id": 1},
        ),
        (
            PlanCommand,
            {"narrative": "yo", "note_id": 1, "user_id": 5, "command_uuid": 100},
            "1 validation error for PlanCommand\ncommand_uuid\n  Input should be a valid string [type=string_type",
            {"narrative": "yo", "note_id": 1, "user_id": 1},
        ),
        (
            PlanCommand,
            {"note_id": 1, "user_id": 5, "narrative": 143},
            "1 validation error for PlanCommand\nnarrative\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 1, "narrative": "143"},
        ),
        (
            PlanCommand,
            {"note_id": 1, "user_id": 5},
            "1 validation error for PlanCommand\nnarrative\n  Field required [type=missing",
            {"note_id": 1, "user_id": 1, "narrative": "143"},
        ),
        (
            PlanCommand,
            {"note_id": 1, "user_id": 5, "narrative": None},
            "1 validation error for PlanCommand\nnarrative\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 1, "narrative": "143"},
        ),
        (
            QuestionnaireCommand,
            {"note_id": 1, "user_id": 1},
            "1 validation error for QuestionnaireCommand\nquestionnaire_id\n  Field required [type=missing",
            {"note_id": 1, "user_id": 1, "questionnaire_id": "500"},
        ),
        (
            QuestionnaireCommand,
            {"note_id": 1, "user_id": 1, "questionnaire_id": None},
            "1 validation error for QuestionnaireCommand\nquestionnaire_id\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 1, "questionnaire_id": "500"},
        ),
        (
            QuestionnaireCommand,
            {"note_id": 1, "user_id": 1, "questionnaire_id": 5},
            "1 validation error for QuestionnaireCommand\nquestionnaire_id\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 1, "questionnaire_id": "500"},
        ),
        (
            QuestionnaireCommand,
            {"note_id": 1, "user_id": 1, "questionnaire_id": "5", "result": 5},
            "1 validation error for QuestionnaireCommand\nresult\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 1, "questionnaire_id": "5"},
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
            {"note_id": 1, "user_id": 1, "medication_id": "500"},
        ),
        (
            StopMedicationCommand,
            {"note_id": 1, "user_id": 1, "medication_id": None},
            "1 validation error for StopMedicationCommand\nmedication_id\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 1, "medication_id": "500"},
        ),
        (
            StopMedicationCommand,
            {"note_id": 1, "user_id": 1, "medication_id": 5},
            "1 validation error for StopMedicationCommand\nmedication_id\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 1, "medication_id": "500"},
        ),
        (
            StopMedicationCommand,
            {"note_id": 1, "user_id": 1, "medication_id": "5", "rationale": 5},
            "1 validation error for StopMedicationCommand\nrationale\n  Input should be a valid string [type=string_type",
            {"note_id": 1, "user_id": 1, "medication_id": "5"},
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
        (
            AssessCommand,
            {"note_id": 1, "user_id": 100, "condition_id": "100"},
            {"note_id": 1, "user_id": 100, "condition_id": "9"},
        ),
        (
            AssessCommand,
            {"note_id": 1, "user_id": 100, "condition_id": "100", "background": "abcdefg"},
            {"note_id": 1, "user_id": 100, "condition_id": "100", "background": None},
        ),
        (
            AssessCommand,
            {
                "note_id": 1,
                "user_id": 100,
                "condition_id": "100",
                "status": AssessCommand.Status.DETERIORATED,
            },
            {"note_id": 1, "user_id": 100, "condition_id": "100", "status": None},
        ),
        (
            AssessCommand,
            {"note_id": 1, "user_id": 100, "condition_id": "100", "narrative": "1234567"},
            {"note_id": 1, "user_id": 100, "condition_id": "100", "narrative": None},
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
            PlanCommand,
            {"narrative": "143", "note_id": 1, "user_id": 100},
            {"narrative": "143", "note_id": 1, "user_id": 7},
        ),
        (
            PlanCommand,
            {"narrative": "143", "command_uuid": "1", "user_id": 100, "note_id": 200},
            {"narrative": "143", "command_uuid": "1", "user_id": 100, "note_id": None},
        ),
        (
            PlanCommand,
            {"narrative": "143", "note_id": 1, "user_id": 100, "command_uuid": "800"},
            {"narrative": "143", "note_id": 1, "user_id": 100, "command_uuid": None},
        ),
        (
            PlanCommand,
            {"note_id": 1, "user_id": 100, "narrative": "123456"},
            {"note_id": 1, "user_id": 100, "narrative": "78900"},
        ),
        (
            QuestionnaireCommand,
            {"note_id": 1, "user_id": 1, "questionnaire_id": "10"},
            {"note_id": 1, "user_id": 1, "questionnaire_id": "1000"},
        ),
        (
            QuestionnaireCommand,
            {"note_id": 1, "user_id": 1, "questionnaire_id": "10", "result": "hi"},
            {"note_id": 1, "user_id": 1, "questionnaire_id": "10", "result": None},
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
            {"note_id": 1, "user_id": 1, "medication_id": "10"},
            {"note_id": 1, "user_id": 1, "medication_id": "1000"},
        ),
        (
            StopMedicationCommand,
            {"note_id": 1, "user_id": 1, "medication_id": "10", "rationale": "hi"},
            {"note_id": 1, "user_id": 1, "medication_id": "10", "rationale": None},
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


@pytest.fixture
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
def command_type_map() -> dict[str, type]:
    return {
        "AutocompleteField": str,
        "MultiLineTextField": str,
        "TextField": str,
        "ChoiceField": str,
        "DateField": datetime,
    }


@pytest.mark.parametrize(
    "Command,uuid",
    [
        (AssessCommand, "446812b3-8486-4e6c-946c-d971a1a247f7"),
        (GoalCommand, "4dd6d032-0da5-4e7f-a834-161161c971d7"),
        (HistoryOfPresentIllnessCommand, "d3f904ba-a425-4605-9030-2eb29673c89d"),
        (MedicationStatementCommand, "1e41d72a-62fb-4d46-83d2-d79d030f54cb"),
        (PlanCommand, "b381862c-4cbf-4ffc-9398-d8a0989a941f"),
        (QuestionnaireCommand, "a6a58bc2-f095-43ee-9cda-edba0db861ac"),
        (ReasonForVisitCommand, "9a9c7a79-816d-4618-a47f-a886a1acc1cf"),
        (StopMedicationCommand, "e041315d-74c7-468d-bac9-b814013123d8"),
    ],
)
def test_command_schema_matches_command_api(
    token: str, command_type_map: dict[str, str], Command: AssessCommand, uuid: str
) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{settings.INTEGRATION_TEST_URL}/core/api/v1/commands/{uuid}/fields/"
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


# Diagnose doesn't have an adapter in home-app

# todo:
#    update canvas_core in home-app
#    deploy to plugin-testing
