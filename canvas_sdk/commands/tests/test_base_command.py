import datetime
import uuid
from enum import Enum

import pytest

from canvas_sdk.commands.base import _BaseCommand


class DummyEnum(Enum):
    """A dummy enum class for testing purposes."""

    LOW = "low"
    HIGH = "high"


class DummyCommand(_BaseCommand):
    """A dummy command class for testing purposes."""

    class Meta:
        key = "dummyCommand"

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
    assert dummy_command_instance.constantized_key() == "DUMMY_COMMAND"
