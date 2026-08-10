import datetime
import json
import uuid
from enum import Enum
from unittest.mock import MagicMock

import pytest
from django.core.exceptions import ImproperlyConfigured
from pydantic_core import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.commands.base import _BaseCommand, _OptionalId
from canvas_sdk.test_utils.factories import NoteFactory, PatientFactory
from canvas_sdk.v1.data import Note, Patient


class DummyEnum(Enum):
    """A dummy enum class for testing purposes."""

    LOW = "low"
    HIGH = "high"


class OptionalIdCommand(_BaseCommand):
    """A command with an optional-id field, for exercising how those fields read a value."""

    class Meta:
        key = "plan"

    record_id: _OptionalId = None


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
    cmd.command_uuid = "b6f4d1c8-31a1-4a0e-9c4b-5a3f4c9d0e21"
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
        "commit": False,
    }


def test_originate_with_commit_true(
    dummy_command_instance: DummyCommand,
) -> None:
    """Test that originate(commit=True) includes commit flag in payload."""
    effect = dummy_command_instance.originate(commit=True)

    assert effect.type == EffectType.ORIGINATE_PLAN_COMMAND
    assert json.loads(effect.payload) == {
        "command": dummy_command_instance.command_uuid,
        "note": dummy_command_instance.note_uuid,
        "data": dummy_command_instance.values,
        "line_number": -1,
        "commit": True,
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
    dummy_command_instance: DummyCommand, stored_command: MagicMock
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
    dummy_command_instance: DummyCommand, stored_command: MagicMock
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
    dummy_command_instance: DummyCommand, stored_command: MagicMock
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
    dummy_command_instance: DummyCommand, stored_command: MagicMock
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


def test_init__raises_error_when_abstract_class() -> None:
    """Test that __init__ raised an error if Meta.abstract is True."""

    # Should not raise an error
    class AbstractCommand(_BaseCommand):
        class Meta:
            abstract = True

    with pytest.raises(TypeError, match="Cannot instantiate abstract class 'AbstractCommand'"):
        AbstractCommand()


def test_set_custom_html_emits_dedicated_effect(
    dummy_command_instance: DummyCommand,
) -> None:
    """set_custom_html(html) emits a SET_COMMAND_CUSTOM_HTML effect with both fields nested in data."""
    dummy_command_instance.command_uuid = "71d20b55-8696-4d04-a848-ce5e0180e00e"
    effect = dummy_command_instance.set_custom_html("<div>plugin html</div>")

    assert effect.type == EffectType.SET_COMMAND_CUSTOM_HTML
    assert json.loads(effect.payload) == {
        "data": {
            "command_id": dummy_command_instance.command_uuid,
            "custom_html": "<div>plugin html</div>",
        },
    }


def test_set_custom_html_transmits_none_to_clear(
    dummy_command_instance: DummyCommand,
) -> None:
    """set_custom_html(None) clears the field."""
    dummy_command_instance.command_uuid = "71d20b55-8696-4d04-a848-ce5e0180e00e"
    payload = json.loads(dummy_command_instance.set_custom_html(None).payload)

    assert payload["data"]["custom_html"] is None


def test_set_custom_html_requires_command_uuid() -> None:
    """set_custom_html() raises if command_uuid is missing."""
    cmd = DummyCommand()

    with pytest.raises(ValueError, match="command_uuid"):
        cmd.set_custom_html("<p>hi</p>")


# --- _is_target_patient: base-class patient-ownership resolution ----------
# `_is_target_patient` lives on the base command and is inherited unchanged by DummyCommand.
# Subclasses use it to refuse a record that belongs to a different patient than the one whose
# chart the command writes to; the patient is resolved from the note or, on an edit, the command.


@pytest.fixture
def patient(db: None) -> Patient:
    """The patient whose chart a command writes to."""
    return PatientFactory.create()


@pytest.fixture
def other_patient(db: None) -> Patient:
    """An unrelated patient, for the cross-patient case."""
    return PatientFactory.create()


@pytest.fixture
def note(patient: Patient) -> Note:
    """A note on the target patient's chart."""
    return NoteFactory.create(patient=patient)


def test_is_target_patient_true_when_the_anchor_resolves_to_that_patient(
    note: Note, patient: Patient
) -> None:
    """The note resolves to its patient, so that patient is the command's target."""
    command = DummyCommand(note_uuid=str(note.id))

    assert command._is_target_patient(str(patient.id)) is True


def test_is_target_patient_false_when_the_anchor_resolves_to_someone_else(
    note: Note, other_patient: Patient
) -> None:
    """A patient other than the one the note resolves to is not the target."""
    command = DummyCommand(note_uuid=str(note.id))

    assert command._is_target_patient(str(other_patient.id)) is False


def test_is_target_patient_true_when_the_anchor_cannot_be_resolved() -> None:
    """With neither a note nor a command to resolve a patient from, nothing is refused.

    Asserted with no database available, so a lookup would raise rather than return; this
    passing is the evidence that none happens.
    """
    assert DummyCommand()._is_target_patient("any-patient-id") is True


# --- _OptionalId: how a command reads an id that may be absent -------------
# Commands that name one of a patient's records share this field type, so it is exercised once here
# rather than in each of them.


def test_an_optional_id_accepts_a_uuid() -> None:
    """The ordinary case."""
    given = uuid.UUID("1b9d6bcd-bbfd-4b2d-9b5d-ab8dfbbd4bed")

    assert OptionalIdCommand(record_id=given).record_id == given


def test_an_optional_id_accepts_a_uuid_given_as_a_string() -> None:
    """Callers pass ids as strings, and lenient parsing is what keeps that working."""
    command = OptionalIdCommand(record_id="1b9d6bcd-bbfd-4b2d-9b5d-ab8dfbbd4bed")  # type: ignore[arg-type]

    assert command.record_id == uuid.UUID("1b9d6bcd-bbfd-4b2d-9b5d-ab8dfbbd4bed")


def test_an_optional_id_refuses_a_value_that_cannot_be_an_id() -> None:
    """The field refuses it, so it never reaches a lookup on an id column.

    Filtering an id column with an unparseable value raises an error the plugin cannot catch, so a
    caller would see a server error instead of a refusal.
    """
    with pytest.raises(ValidationError):
        OptionalIdCommand(record_id="99999")  # type: ignore[arg-type]


@pytest.mark.parametrize("given", ["", "   "])
def test_an_optional_id_reads_a_blank_value_as_absent(given: str) -> None:
    """These fields took a string before they took a UUID, so a caller may send "" for "nothing".

    That has to keep meaning absent rather than becoming a validation error.
    """
    assert OptionalIdCommand(record_id=given).record_id is None  # type: ignore[arg-type]


def test_an_optional_id_reads_a_blank_value_assigned_later_as_absent() -> None:
    """`validate_assignment` is on, so the same reading holds when the field is set."""
    command = OptionalIdCommand()

    command.record_id = ""  # type: ignore[assignment]

    assert command.record_id is None
