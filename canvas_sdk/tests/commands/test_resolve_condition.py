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
