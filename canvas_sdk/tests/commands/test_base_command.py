import datetime
import json
import uuid
from enum import Enum

import pytest

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.commands.base import _BaseCommand


class DummyEnum(Enum):
    """A dummy enum class for testing purposes."""

    LOW = "low"
    HIGH = "high"


class DummyCommand(_BaseCommand):
    """A dummy command class for testing purposes."""

    class Meta:
        key = "plan"

    # Fields
    int_field: int = 0
    str_field: str = ""
    enum_field: DummyEnum | None = None
    date_field: datetime.date | None = None
    uuid_field: uuid.UUID | None = None


@pytest.fixture
def dummy_command_instance() -> DummyCommand:
    """Fixture to return a mock instance of DummyCommand for testing."""
    cmd = DummyCommand(int_field=10, str_field="hello")
    # Set additional fields after instantiation.
    cmd.enum_field = DummyEnum.HIGH
    cmd.date_field = datetime.date(2025, 2, 14)
    cmd.uuid_field = uuid.UUID("12345678-1234-5678-1234-567812345678")
    # Set note_uuid and command_uuid for effect methods.
    cmd.note_uuid = "note-123"
    cmd.command_uuid = "cmd-456"
    return cmd


def test_dirty_keys(dummy_command_instance: DummyCommand) -> None:
    """Test that the dirty_keys property correctly tracks all fields that are set (via constructor and subsequent assignment)."""
    keys = set(dummy_command_instance._dirty_keys)
    expected_keys = {"int_field", "str_field", "enum_field", "date_field", "uuid_field"}
    assert expected_keys == keys


def test_values_transformation(dummy_command_instance: DummyCommand) -> None:
    """
    Test that the values property applies type-specific transformations:
    - Enums are replaced by their .value.
    - Date/datetime fields are converted to ISO formatted strings.
    - UUID fields are converted to strings.
    - Other types are returned as-is.
    """
    vals = dummy_command_instance.values
    assert vals["int_field"] == 10
    assert vals["str_field"] == "hello"
    # For enum_field, should return its .value.
    assert vals["enum_field"] == DummyEnum.HIGH.value
    # For date_field, should return an ISO string.

    assert (
        vals["date_field"] == dummy_command_instance.date_field.isoformat()
        if dummy_command_instance.date_field
        else None
    )
    # For uuid_field, should return a string.
    assert vals["uuid_field"] == str(dummy_command_instance.uuid_field)


def test_constantized_key(dummy_command_instance: DummyCommand) -> None:
    """
    Test that constantized_key transforms the Meta.key from 'dummyCommand'
    into an uppercase, underscore-separated string ('DUMMY_COMMAND').
    """
    assert dummy_command_instance.constantized_key() == "PLAN"


def test_originate_successfully_returns_originate_effect(
    dummy_command_instance: DummyCommand,
) -> None:
    """Test that originate() successfully returns the originate effect."""
    effect = dummy_command_instance.originate()

    assert effect is not None
    assert effect.type == EffectType.ORIGINATE_PLAN_COMMAND
    assert json.loads(effect.payload) == {
        "command": dummy_command_instance.command_uuid,
        "note": dummy_command_instance.note_uuid,
        "data": dummy_command_instance.values,
        "line_number": -1,
    }


def test_originate_raises_error_when_required_fields_not_set() -> None:
    """Test that originate() raises an error when a required field is not set."""
    cmd = DummyCommand()

    with pytest.raises(ValueError, match="note_uuid"):
        cmd.originate()


def test_commit_successfully_returns_commit_effect(
    dummy_command_instance: DummyCommand,
) -> None:
    """Test that commit() successfully returns the commit effect."""
    effect = dummy_command_instance.commit()

    assert effect is not None
    assert effect.type == EffectType.COMMIT_PLAN_COMMAND
    assert json.loads(effect.payload) == {
        "command": dummy_command_instance.command_uuid,
    }


def test_commit_raises_error_when_required_fields_not_set() -> None:
    """Test that commit() raises an error when a required field is not set."""
    cmd = DummyCommand(str_field="hello")

    with pytest.raises(ValueError, match="command_uuid"):
        cmd.commit()


def test_edit_successfully_returns_edit_effect(
    dummy_command_instance: DummyCommand,
) -> None:
    """Test that edit() successfully returns the edit effect."""
    dummy_command_instance.int_field = 1
    effect = dummy_command_instance.edit()

    assert effect is not None
    assert effect.type == EffectType.EDIT_PLAN_COMMAND
    assert json.loads(effect.payload) == {
        "command": dummy_command_instance.command_uuid,
        "data": dummy_command_instance.values,
    }


def test_edit_raises_error_when_required_fields_not_set() -> None:
    """Test that edit() raises an error when a required field is not set."""
    cmd = DummyCommand(str_field="hello")
    cmd.int_field = 1

    with pytest.raises(ValueError, match="command_uuid"):
        cmd.edit()


def test_delete_successfully_returns_delete_effect(
    dummy_command_instance: DummyCommand,
) -> None:
    """Test that delete() successfully returns the delete effect."""
    effect = dummy_command_instance.delete()

    assert effect is not None
    assert effect.type == EffectType.DELETE_PLAN_COMMAND
    assert json.loads(effect.payload) == {
        "command": dummy_command_instance.command_uuid,
    }


def test_delete_raises_error_when_required_fields_not_set() -> None:
    """Test that delete() raises an error when a required field is not set."""
    cmd = DummyCommand(str_field="hello")

    with pytest.raises(ValueError, match="command_uuid"):
        cmd.delete()


def test_enter_in_error_successfully_returns_enter_in_error_effect(
    dummy_command_instance: DummyCommand,
) -> None:
    """Test that enter_in_error() successfully returns the enter_in_error effect."""
    effect = dummy_command_instance.enter_in_error()

    assert effect is not None
    assert effect.type == EffectType.ENTER_IN_ERROR_PLAN_COMMAND
    assert json.loads(effect.payload) == {
        "command": dummy_command_instance.command_uuid,
    }


def test_enter_in_error_raises_error_when_required_fields_not_set() -> None:
    """Test that enter_in_error() raises an error when a required field is not set."""
    cmd = DummyCommand(str_field="hello")

    with pytest.raises(ValueError, match="command_uuid"):
        cmd.enter_in_error()


def test_chaining_originate_and_commit_with_user_set_uuid() -> None:
    """Test that originate() and commit() can be chained when command_uuid is set manually."""
    # Create command with note_uuid required for originate
    cmd = DummyCommand(str_field="test")
    cmd.note_uuid = "note-123"
    
    # Set command_uuid manually for chaining
    test_uuid = str(uuid.uuid4())
    cmd.command_uuid = test_uuid
    
    # Both methods should work without raising errors
    originate_effect = cmd.originate()
    commit_effect = cmd.commit()
    
    # Verify originate effect
    assert originate_effect.type == EffectType.ORIGINATE_PLAN_COMMAND
    originate_payload = json.loads(originate_effect.payload)
    assert originate_payload["command"] == test_uuid
    assert originate_payload["note"] == "note-123"
    
    # Verify commit effect
    assert commit_effect.type == EffectType.COMMIT_PLAN_COMMAND
    commit_payload = json.loads(commit_effect.payload)
    assert commit_payload["command"] == test_uuid


def test_chaining_originate_and_commit_without_command_uuid_fails() -> None:
    """Test that commit() fails when command_uuid is not set, even if originate() would work."""
    cmd = DummyCommand(str_field="test")
    cmd.note_uuid = "note-123"
    # Don't set command_uuid
    
    # originate() should work
    originate_effect = cmd.originate()
    assert originate_effect is not None
    
    # But commit() should fail
    with pytest.raises(ValueError, match="command_uuid"):
        cmd.commit()
