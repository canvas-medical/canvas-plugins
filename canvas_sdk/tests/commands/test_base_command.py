import datetime
import json
import uuid
from abc import ABC
from enum import Enum

import pytest
from django.core.exceptions import ImproperlyConfigured

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


def test_batch_originate_successfully_returns_dict(
    dummy_command_instance: DummyCommand,
) -> None:
    """Test that _origination_payload_for_batch() successfully returns the correct dict."""
    batch_payload = dummy_command_instance._origination_payload_for_batch()

    assert batch_payload == {
        "type": "ORIGINATE_PLAN_COMMAND",
        "command": dummy_command_instance.command_uuid,
        "note": dummy_command_instance.note_uuid,
        "data": dummy_command_instance.values,
        "line_number": -1,
    }


def test_batch_originate_raises_error_when_required_fields_not_set() -> None:
    """Test that _origination_payload_for_batch() raises an error when a required field is not set."""
    cmd = DummyCommand()

    with pytest.raises(ValueError, match="note_uuid"):
        cmd._origination_payload_for_batch()


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


def test_init_subclass_raises_error_when_meta_key_missing() -> None:
    """Test that __init_subclass__ raises an error when Meta.key is missing on a concrete (non-ABC) class."""
    with pytest.raises(ImproperlyConfigured, match="must specify Meta.key"):

        class CommandWithoutKey(_BaseCommand):
            pass


def test_init_subclass_raises_error_when_meta_key_empty() -> None:
    """Test that __init_subclass__ raises an error when Meta.key is an empty string on a concrete class."""
    with pytest.raises(ImproperlyConfigured, match="must specify Meta.key"):

        class CommandWithEmptyKey(_BaseCommand):
            class Meta:
                key = ""


def test_init_subclass_allows_abc_without_meta_key() -> None:
    """Test that __init_subclass__ allows abstract base classes (ABC) to not have Meta.key."""

    # Should not raise an error
    class AbstractCommand(_BaseCommand, ABC):
        pass

    # Verify we can create the abstract class without errors
    assert issubclass(AbstractCommand, _BaseCommand)
    assert issubclass(AbstractCommand, ABC)
