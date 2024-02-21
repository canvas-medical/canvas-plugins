from datetime import datetime

import pytest
from pydantic import ValidationError

from canvas_sdk.commands import AssessCommand, DiagnoseCommand, PlanCommand
from canvas_sdk.commands.assess.assess import AssessStatus


@pytest.mark.parametrize(
    "Command,err_kwargs,err_msg,valid_kwargs",
    [
        (
            PlanCommand,
            {},
            "1 validation error for PlanCommand\nuser_id\n  Field required [type=missing, input_value={}, input_type=dict]",
            {"user_id": 1},
        ),
        (
            PlanCommand,
            {"user_id": None},
            "1 validation error for PlanCommand\nuser_id\n  Input should be a valid integer [type=int_type, input_value=None, input_type=NoneType]",
            {"user_id": 1},
        ),
        (
            PlanCommand,
            {"user_id": "5"},
            "1 validation error for PlanCommand\nuser_id\n  Input should be a valid integer [type=int_type, input_value='5', input_type=str]",
            {"user_id": 1},
        ),
        (
            PlanCommand,
            {"user_id": 5, "note_id": "100"},
            "1 validation error for PlanCommand\nnote_id\n  Input should be a valid integer [type=int_type, input_value='100', input_type=str]",
            {"user_id": 1},
        ),
        (
            PlanCommand,
            {"user_id": 5, "command_uuid": 100},
            "1 validation error for PlanCommand\ncommand_uuid\n  Input should be a valid string [type=string_type, input_value=100, input_type=int]",
            {"user_id": 1},
        ),
        (
            PlanCommand,
            {"user_id": 5, "narrative": 143},
            "1 validation error for PlanCommand\nnarrative\n  Input should be a valid string [type=string_type, input_value=143, input_type=int]",
            {"user_id": 1},
        ),
        (
            AssessCommand,
            {"user_id": 5},
            "1 validation error for AssessCommand\ncondition_id\n  Field required [type=missing, input_value={'user_id': 5}, input_type=dict]",
            {"user_id": 1, "condition_id": 100},
        ),
        (
            AssessCommand,
            {"user_id": 5, "condition_id": None},
            "1 validation error for AssessCommand\ncondition_id\n  Input should be a valid integer [type=int_type, input_value=None, input_type=NoneType]",
            {"user_id": 1, "condition_id": 100},
        ),
        (
            AssessCommand,
            {"user_id": 5, "condition_id": "h"},
            "1 validation error for AssessCommand\ncondition_id\n  Input should be a valid integer [type=int_type, input_value='h', input_type=str]",
            {"user_id": 1, "condition_id": 100},
        ),
        (
            AssessCommand,
            {"user_id": 5, "condition_id": 100, "background": 100},
            "1 validation error for AssessCommand\nbackground\n  Input should be a valid string [type=string_type, input_value=100, input_type=int]",
            {"user_id": 1, "condition_id": 100},
        ),
        (
            AssessCommand,
            {"user_id": 5, "condition_id": 100, "status": "active"},
            "1 validation error for AssessCommand\nstatus\n  Input should be an instance of AssessStatus [type=is_instance_of, input_value='active', input_type=str]",
            {"user_id": 1, "condition_id": 100},
        ),
        (
            AssessCommand,
            {"user_id": 5, "condition_id": 100, "narrative": 1},
            "1 validation error for AssessCommand\nnarrative\n  Input should be a valid string [type=string_type, input_value=1, input_type=int]",
            {"user_id": 1, "condition_id": 100},
        ),
        (
            DiagnoseCommand,
            {"user_id": 5},
            "1 validation error for DiagnoseCommand\nicd10_code\n  Field required [type=missing, input_value={'user_id': 5}, input_type=dict]",
            {"user_id": 1, "icd10_code": "Z00"},
        ),
        (
            DiagnoseCommand,
            {"user_id": 5, "icd10_code": None},
            "1 validation error for DiagnoseCommand\nicd10_code\n  Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]",
            {"user_id": 1, "icd10_code": "Z00"},
        ),
        (
            DiagnoseCommand,
            {"user_id": 5, "icd10_code": 1},
            "1 validation error for DiagnoseCommand\nicd10_code\n  Input should be a valid string [type=string_type, input_value=1, input_type=int]",
            {"user_id": 1, "icd10_code": "Z00"},
        ),
        (
            DiagnoseCommand,
            {"user_id": 5, "icd10_code": "Z00", "background": 1},
            "1 validation error for DiagnoseCommand\nbackground\n  Input should be a valid string [type=string_type, input_value=1, input_type=int]",
            {"user_id": 1, "icd10_code": "Z00"},
        ),
        (
            DiagnoseCommand,
            {"user_id": 5, "icd10_code": "Z00", "approximate_date_of_onset": 1},
            "1 validation error for DiagnoseCommand\napproximate_date_of_onset\n  Input should be a valid datetime [type=datetime_type, input_value=1, input_type=int]",
            {"user_id": 1, "icd10_code": "Z00"},
        ),
        (
            DiagnoseCommand,
            {"user_id": 5, "icd10_code": "Z00", "approximate_date_of_onset": "1"},
            "1 validation error for DiagnoseCommand\napproximate_date_of_onset\n  Input should be a valid datetime [type=datetime_type, input_value='1', input_type=str]",
            {"user_id": 1, "icd10_code": "Z00"},
        ),
        (
            DiagnoseCommand,
            {"user_id": 5, "icd10_code": "Z00", "today_assessment": 1},
            "1 validation error for DiagnoseCommand\ntoday_assessment\n  Input should be a valid string [type=string_type, input_value=1, input_type=int]",
            {"user_id": 1, "icd10_code": "Z00"},
        ),
    ],
)
def test_command_raises_error_when_kwarg_given_incorrect_type(
    Command: PlanCommand | AssessCommand | DiagnoseCommand,
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
        (PlanCommand, {"user_id": 100}, {"user_id": 7}),
        (PlanCommand, {"user_id": 100, "note_id": 200}, {"user_id": 100, "note_id": None}),
        (
            PlanCommand,
            {"user_id": 100, "command_uuid": "800"},
            {"user_id": 100, "command_uuid": None},
        ),
        (
            PlanCommand,
            {"user_id": 100, "narrative": "123456"},
            {"user_id": 100, "narrative": None},
        ),
        (
            AssessCommand,
            {"user_id": 100, "condition_id": 100},
            {"user_id": 100, "condition_id": 9},
        ),
        (
            AssessCommand,
            {"user_id": 100, "condition_id": 100, "background": "abcdefg"},
            {"user_id": 100, "condition_id": 100, "background": None},
        ),
        (
            AssessCommand,
            {"user_id": 100, "condition_id": 100, "status": AssessStatus.DETERIORATED},
            {"user_id": 100, "condition_id": 100, "status": None},
        ),
        (
            AssessCommand,
            {"user_id": 100, "condition_id": 100, "narrative": "1234567"},
            {"user_id": 100, "condition_id": 100, "narrative": None},
        ),
        (
            DiagnoseCommand,
            {"user_id": 1, "icd10_code": "Z00"},
            {"user_id": 1, "icd10_code": "400"},
        ),
        (
            DiagnoseCommand,
            {"user_id": 1, "icd10_code": "Z00", "background": "123"},
            {"user_id": 1, "icd10_code": "Z00", "background": None},
        ),
        (
            DiagnoseCommand,
            {"user_id": 1, "icd10_code": "Z00", "approximate_date_of_onset": datetime.now()},
            {"user_id": 1, "icd10_code": "Z00", "approximate_date_of_onset": None},
        ),
        (
            DiagnoseCommand,
            {"user_id": 1, "icd10_code": "Z00", "today_assessment": "hi"},
            {"user_id": 1, "icd10_code": "Z00", "today_assessment": None},
        ),
    ],
)
def test_command_allows_kwarg_with_correct_type(
    Command: PlanCommand | AssessCommand | DiagnoseCommand,
    test_init_kwarg: dict,
    test_updated_value: dict,
) -> None:
    cmd = Command(**test_init_kwarg)

    init_k, init_v = list(test_init_kwarg.items())[-1]
    assert getattr(cmd, init_k) == init_v

    updated_k, updated_v = list(test_updated_value.items())[-1]
    setattr(cmd, updated_k, updated_v)
    assert getattr(cmd, updated_k) == updated_v
