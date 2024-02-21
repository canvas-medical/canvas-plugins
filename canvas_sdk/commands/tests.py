import pytest
from pydantic import ValidationError

from canvas_sdk.commands import AssessCommand, PlanCommand
from canvas_sdk.commands.assess.assess import AssessStatus


@pytest.mark.parametrize(
    "Command,err_kwargs,err_msg",
    [
        (
            PlanCommand,
            {},
            "1 validation error for PlanCommand\nuser_id\n  Field required [type=missing, input_value={}, input_type=dict]",
        ),
        (
            PlanCommand,
            {"user_id": None},
            "1 validation error for PlanCommand\nuser_id\n  Input should be a valid integer [type=int_type, input_value=None, input_type=NoneType]",
        ),
        (
            PlanCommand,
            {"user_id": "5"},
            "1 validation error for PlanCommand\nuser_id\n  Input should be a valid integer [type=int_type, input_value='5', input_type=str]",
        ),
        (
            PlanCommand,
            {"user_id": 5, "note_id": "100"},
            "1 validation error for PlanCommand\nnote_id\n  Input should be a valid integer [type=int_type, input_value='100', input_type=str]",
        ),
        (
            PlanCommand,
            {"user_id": 5, "command_uuid": 100},
            "1 validation error for PlanCommand\ncommand_uuid\n  Input should be a valid string [type=string_type, input_value=100, input_type=int]",
        ),
        (
            PlanCommand,
            {"user_id": 5, "narrative": 143},
            "1 validation error for PlanCommand\nnarrative\n  Input should be a valid string [type=string_type, input_value=143, input_type=int]",
        ),
        (
            AssessCommand,
            {"user_id": 5, "condition_id": "h"},
            "1 validation error for AssessCommand\ncondition_id\n  Input should be a valid integer [type=int_type, input_value='h', input_type=str]",
        ),
        (
            AssessCommand,
            {"user_id": 5, "background": 100},
            "1 validation error for AssessCommand\nbackground\n  Input should be a valid string [type=string_type, input_value=100, input_type=int]",
        ),
        (
            AssessCommand,
            {"user_id": 5, "status": "active"},
            "1 validation error for AssessCommand\nstatus\n  Input should be an instance of AssessStatus [type=is_instance_of, input_value='active', input_type=str]",
        ),
        (
            AssessCommand,
            {"user_id": 5, "narrative": 1},
            "1 validation error for AssessCommand\nnarrative\n  Input should be a valid string [type=string_type, input_value=1, input_type=int]",
        ),
    ],
)
def test_command_raises_error_when_kwarg_given_incorrect_type(
    Command: PlanCommand | AssessCommand, err_kwargs: dict, err_msg: str
) -> None:
    with pytest.raises(ValidationError) as e1:
        Command(**err_kwargs)
    assert err_msg in repr(e1.value)

    plan = Command(user_id=1)
    if not err_kwargs:
        return
    key, value = list(err_kwargs.items())[-1]
    with pytest.raises(ValidationError) as e2:
        setattr(plan, key, value)
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
            {"user_id": 100, "condition_id": None},
        ),
        (
            AssessCommand,
            {"user_id": 100, "background": "abcdefg"},
            {"user_id": 100, "background": None},
        ),
        (
            AssessCommand,
            {"user_id": 100, "status": AssessStatus.DETERIORATED},
            {"user_id": 100, "status": None},
        ),
        (
            AssessCommand,
            {"user_id": 100, "narrative": "1234567"},
            {"user_id": 100, "narrative": None},
        ),
    ],
)
def test_command_allows_kwarg_with_correct_type(
    Command: PlanCommand | AssessCommand, test_init_kwarg: dict, test_updated_value: dict
) -> None:
    plan = Command(**test_init_kwarg)

    init_k, init_v = list(test_init_kwarg.items())[-1]
    assert getattr(plan, init_k) == init_v

    updated_k, updated_v = list(test_updated_value.items())[-1]
    setattr(plan, updated_k, updated_v)
    assert getattr(plan, updated_k) == updated_v
