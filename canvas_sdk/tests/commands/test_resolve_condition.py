import datetime
from uuid import uuid4

import pytest
from pydantic_core import ValidationError

from canvas_sdk.commands import ResolveConditionCommand
from canvas_sdk.test_utils.factories import NoteFactory, PatientFactory
from canvas_sdk.v1.data import Command, Condition, Note, Patient


@pytest.fixture
def patient(db: None) -> Patient:
    """A patient who owns the note the command is charted in."""
    return PatientFactory.create()


@pytest.fixture
def other_patient(db: None) -> Patient:
    """An unrelated patient, used to build a cross-patient condition."""
    return PatientFactory.create()


@pytest.fixture
def note(patient: Patient) -> Note:
    """A note belonging to `patient`."""
    return NoteFactory.create(patient=patient)


def _condition(patient: Patient, clinical_status: str = "active") -> Condition:
    """Create a minimal condition for the given patient."""
    return Condition.objects.create(
        patient=patient,
        deleted=False,
        onset_date=datetime.date(2024, 1, 1),
        resolution_date=datetime.date(2024, 1, 1),
        clinical_status=clinical_status,
        notes="",
        surgical=False,
    )


@pytest.fixture
def condition(patient: Patient) -> Condition:
    """A condition belonging to the same patient as the note."""
    return _condition(patient)


@pytest.fixture
def foreign_condition(other_patient: Patient) -> Condition:
    """A condition belonging to a different patient than the note."""
    return _condition(other_patient)


@pytest.fixture
def command(note: Note) -> Command:
    """A persisted resolveCondition command anchored to `note`, for exercising edit()."""
    return Command.objects.create(
        note=note,
        patient=note.patient,
        state="staged",
        schema_key="resolveCondition",
        data={},
        origination_source="plugin",
        anchor_object_type="",
        anchor_object_dbid=0,
    )


# --- condition ownership on originate -------------------------------------


def test_originate_accepts_condition_belonging_to_the_notes_patient(
    note: Note, condition: Condition
) -> None:
    """The ordinary case: the id names one of this patient's conditions."""
    command = ResolveConditionCommand(note_uuid=str(note.id), condition_id=condition.id)

    assert command.originate()


def test_originate_rejects_condition_belonging_to_another_patient(
    note: Note, foreign_condition: Condition
) -> None:
    """A real condition, but not this patient's."""
    command = ResolveConditionCommand(note_uuid=str(note.id), condition_id=foreign_condition.id)

    with pytest.raises(ValidationError) as caught:
        command.originate()

    assert "does not belong to this command's patient" in str(caught.value)


def test_originate_rejects_an_unknown_condition(note: Note) -> None:
    """A well-formed id that names nothing."""
    command = ResolveConditionCommand(note_uuid=str(note.id), condition_id=uuid4())

    with pytest.raises(ValidationError):
        command.originate()


def test_a_resolved_condition_is_still_accepted(note: Note, patient: Patient) -> None:
    """Only ownership is checked, not the condition's clinical status.

    Narrowing to active conditions would refuse ones that can be stored, so the check stays at
    what the record itself requires: it exists, and it is this patient's.
    """
    resolved = _condition(patient, clinical_status="resolved")
    command = ResolveConditionCommand(note_uuid=str(note.id), condition_id=resolved.id)

    assert command.originate()


# --- condition ownership on edit ------------------------------------------


def test_edit_accepts_condition_belonging_to_the_commands_patient(
    command: Command, condition: Condition
) -> None:
    """The bug this fixes: an edit names a command, not a note.

    Resolving the patient from `note_uuid` alone left nothing to compare against on this path, so
    every edit that named a condition was refused.
    """
    edit = ResolveConditionCommand(command_uuid=str(command.id), condition_id=condition.id)

    assert edit.edit()


def test_edit_rejects_condition_belonging_to_another_patient(
    command: Command, foreign_condition: Condition
) -> None:
    """The other half: resolving through the command still refuses a foreign condition."""
    edit = ResolveConditionCommand(command_uuid=str(command.id), condition_id=foreign_condition.id)

    with pytest.raises(ValidationError):
        edit.edit()


# --- cases with nothing to check ------------------------------------------


def test_no_condition_id_means_nothing_to_check(note: Note) -> None:
    """The field is optional, so an empty command originates fine."""
    assert ResolveConditionCommand(note_uuid=str(note.id)).originate()


def test_an_id_that_cannot_be_an_id_is_a_validation_error(note: Note) -> None:
    """`condition_id` is a UUID, so a malformed value is refused by the field.

    It matters that this is the field's error rather than the database's: filtering an id column with
    an unparseable value raises an error the plugin cannot catch, so the caller would see a server
    error instead of a refusal.
    """
    with pytest.raises(ValidationError):
        ResolveConditionCommand(note_uuid=str(note.id), condition_id="99999")  # type: ignore[arg-type]


def test_an_id_given_as_a_string_is_still_accepted(note: Note, condition: Condition) -> None:
    """Callers pass ids as strings, and lenient parsing is what keeps that working.

    The field was `UUID | str` before this, so a string is exactly what its callers have been
    passing; narrowing it to UUID only stays compatible because values are read leniently.
    """
    command = ResolveConditionCommand(
        note_uuid=str(note.id),
        condition_id=str(condition.id),  # type: ignore[arg-type]
    )

    assert command.originate()


def test_a_command_with_neither_anchor_skips_the_check(condition: Condition) -> None:
    """A command that cannot know its patient must not guess.

    A plugin can return several effects from one handler, and the note a later effect names may not
    be persisted when that effect is built.
    """
    command = ResolveConditionCommand(condition_id=condition.id)

    assert command._anchor_patient_id() is None


# --- rationale ------------------------------------------------------------


def test_rationale_accepts_max_length() -> None:
    """Rationale accepts a value at the 1024 character limit."""
    assert ResolveConditionCommand(note_uuid="n", rationale="a" * 1024).rationale == "a" * 1024


def test_rationale_rejects_above_max_length() -> None:
    """Rationale rejects a value over the 1024 character limit."""
    with pytest.raises(ValidationError):
        ResolveConditionCommand(note_uuid="n", rationale="a" * 1025)


@pytest.mark.parametrize("given", ["", "   "])
def test_a_blank_id_is_read_as_no_id(note: Note, given: str) -> None:
    """The field took a string before it took a UUID, so a caller may send "" for "nothing".

    That has to keep meaning absent rather than becoming a validation error, and there is then no
    ownership to check.
    """
    command = ResolveConditionCommand(note_uuid=str(note.id), condition_id=given)  # type: ignore[arg-type]

    assert command.condition_id is None
    assert command.originate()


def test_a_blank_id_assigned_later_is_also_read_as_no_id(note: Note) -> None:
    """`validate_assignment` is on, so the same reading has to hold when the field is set."""
    command = ResolveConditionCommand(note_uuid=str(note.id))

    command.condition_id = ""  # type: ignore[assignment]

    assert command.condition_id is None
