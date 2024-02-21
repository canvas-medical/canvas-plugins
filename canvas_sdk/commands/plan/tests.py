import pytest
from pydantic import ValidationError

from canvas_sdk.commands import PlanCommand


def test_plan_command_init_raises_error_without_user_id() -> None:
    with pytest.raises(ValidationError) as e:
        PlanCommand()
    assert (
        "1 validation error for PlanCommand\nuser_id\n  Field required [type=missing, input_value={}, input_type=dict]"
        in repr(e.value)
    )


def test_plan_command_init_sets_all_kwargs_with_correct_type() -> None:
    p = PlanCommand(user_id=1, note_id=100, command_uuid="123", narrative="hello in there")
    assert p.__dict__ == {
        "user_id": 1,
        "note_id": 100,
        "command_uuid": "123",
        "narrative": "hello in there",
    }


def test_plan_command_init_sets_all_kwargs_with_correct_none_type() -> None:
    p = PlanCommand(user_id=1)
    assert p.__dict__ == {
        "user_id": 1,
        "note_id": None,
        "command_uuid": None,
        "narrative": None,
    }


def test_plan_command_raises_error_when_wrong_type_is_set_on_user_id() -> None:
    with pytest.raises(ValidationError) as e:
        PlanCommand(user_id="1", note_id=100, command_uuid="123", narrative="hello in there")
    assert (
        "1 validation error for PlanCommand\nuser_id\n  Input should be a valid integer [type=int_type, input_value='1', input_type=str]"
        in repr(e.value)
    )


def test_plan_command_raises_error_when_wrong_type_is_set_on_note_id() -> None:
    with pytest.raises(ValidationError) as e:
        PlanCommand(user_id=1, note_id="100", command_uuid="123", narrative="hello in there")
    assert (
        "1 validation error for PlanCommand\nnote_id\n  Input should be a valid integer [type=int_type, input_value='100', input_type=str]"
        in repr(e.value)
    )


def test_plan_command_raises_error_when_wrong_type_is_set_on_command_uuid() -> None:
    with pytest.raises(ValidationError) as e:
        PlanCommand(user_id=1, note_id=100, command_uuid=123, narrative="hello in there")
    assert (
        "1 validation error for PlanCommand\ncommand_uuid\n  Input should be a valid string [type=string_type, input_value=123, input_type=int]"
        in repr(e.value)
    )


def test_plan_command_raises_error_when_wrong_type_is_set_on_narrative() -> None:
    with pytest.raises(ValidationError) as e:
        PlanCommand(user_id=1, note_id=100, command_uuid="123", narrative=143)
    assert (
        "1 validation error for PlanCommand\nnarrative\n  Input should be a valid string [type=string_type, input_value=143, input_type=int]"
        in repr(e.value)
    )


def test_plan_command_only_allows_defined_type_to_be_set_on_user_id() -> None:
    p = PlanCommand(user_id=1)
    with pytest.raises(ValidationError) as e1:
        p.user_id = "1"
    assert (
        "1 validation error for PlanCommand\nuser_id\n  Input should be a valid integer [type=int_type, input_value='1', input_type=str]"
        in repr(e1.value)
    )

    with pytest.raises(ValidationError) as e2:
        p.user_id = None
    assert (
        "1 validation error for PlanCommand\nuser_id\n  Input should be a valid integer [type=int_type, input_value=None, input_type=NoneType]"
        in repr(e2.value)
    )

    p.user_id = 100
    assert p.user_id == 100


def test_plan_command_only_allows_defined_type_to_be_set_on_note_id() -> None:
    p = PlanCommand(user_id=1)
    with pytest.raises(ValidationError) as e:
        p.note_id = "1"
    assert (
        "1 validation error for PlanCommand\nnote_id\n  Input should be a valid integer [type=int_type, input_value='1', input_type=str]"
        in repr(e.value)
    )

    p.note_id = 100
    assert p.note_id == 100

    p.note_id = None
    assert p.note_id is None


def test_plan_command_only_allows_defined_type_to_be_set_on_command_uuid() -> None:
    p = PlanCommand(user_id=1)
    with pytest.raises(ValidationError) as e:
        p.command_uuid = 1
    assert (
        "1 validation error for PlanCommand\ncommand_uuid\n  Input should be a valid string [type=string_type, input_value=1, input_type=int]"
        in repr(e.value)
    )

    p.command_uuid = "100"
    assert p.command_uuid == "100"

    p.command_uuid = None
    assert p.command_uuid is None


def test_plan_command_only_allows_defined_type_to_be_set_on_narrative() -> None:
    p = PlanCommand(user_id=1)
    with pytest.raises(ValidationError) as e:
        p.narrative = 1
    assert (
        "1 validation error for PlanCommand\nnarrative\n  Input should be a valid string [type=string_type, input_value=1, input_type=int]"
        in repr(e.value)
    )

    p.narrative = "yeah"
    assert p.narrative == "yeah"

    p.narrative = None
    assert p.narrative is None
