import datetime

import pytest
from pydantic_core import ValidationError

from canvas_sdk.commands import AssessCommand
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


def _condition(patient: Patient | None) -> Condition:
    """Create a minimal active condition for the given patient."""
    return Condition.objects.create(
        patient=patient,
        deleted=False,
        onset_date=datetime.date(2024, 1, 1),
        resolution_date=datetime.date(2024, 1, 1),
        clinical_status="active",
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
    """A persisted assess command anchored to `note`, for exercising edit()."""
    return Command.objects.create(
        note=note,
        patient=note.patient,
        state="staged",
        schema_key="assess",
        data={},
        origination_source="plugin",
        anchor_object_type="",
        anchor_object_dbid=0,
    )


# --- narrative max length -------------------------------------------------


def test_narrative_accepts_max_length() -> None:
    """Narrative accepts a value at the 2048 character limit."""
    assert AssessCommand(note_uuid="n", narrative="a" * 2048).narrative == "a" * 2048


def test_narrative_rejects_above_max_length() -> None:
    """Narrative rejects a value over the 2048 character limit."""
    with pytest.raises(ValidationError):
        AssessCommand(note_uuid="n", narrative="a" * 2049)


def test_narrative_rejects_above_max_length_on_assignment() -> None:
    """Narrative is validated when assigned after construction."""
    assess = AssessCommand(note_uuid="n")
    with pytest.raises(ValidationError):
        assess.narrative = "a" * 2049


def test_narrative_defaults_to_none() -> None:
    """Narrative defaults to None."""
    assert AssessCommand(note_uuid="n").narrative is None


# --- condition ownership on originate -------------------------------------


def test_originate_accepts_condition_belonging_to_the_notes_patient(
    note: Note, condition: Condition
) -> None:
    """A condition on the note's own patient originates without error."""
    effect = AssessCommand(note_uuid=str(note.id), condition_id=str(condition.id)).originate()

    assert effect is not None


def test_originate_rejects_condition_belonging_to_another_patient(
    note: Note, foreign_condition: Condition
) -> None:
    """A condition on a different patient is rejected before an effect is emitted."""
    assess = AssessCommand(note_uuid=str(note.id), condition_id=str(foreign_condition.id))

    with pytest.raises(ValidationError, match="does not belong to this command's patient"):
        assess.originate()


def test_originate_rejects_unknown_condition(note: Note) -> None:
    """A condition_id that matches no condition is rejected like any foreign condition."""
    assess = AssessCommand(
        note_uuid=str(note.id), condition_id="8bcb9b2e-0f3e-4f9a-9d9a-4b2c1f7d0a11"
    )

    with pytest.raises(ValidationError, match="does not belong to this command's patient"):
        assess.originate()


def test_originate_rejects_condition_with_no_patient(note: Note) -> None:
    """A condition charted against no patient is rejected; patient is nullable."""
    orphan = _condition(patient=None)
    assess = AssessCommand(note_uuid=str(note.id), condition_id=str(orphan.id))

    with pytest.raises(ValidationError, match="does not belong to this command's patient"):
        assess.originate()


def test_originate_without_condition_id_is_unvalidated(note: Note) -> None:
    """Omitting condition_id skips the ownership check entirely."""
    effect = AssessCommand(note_uuid=str(note.id), narrative="No condition yet").originate()

    assert effect is not None


def test_originate_allows_condition_when_note_is_not_yet_persisted(condition: Condition) -> None:
    """A not-yet-persisted note doesn't cause its condition to be rejected."""
    assess = AssessCommand(
        note_uuid="3f7c1a9e-2b6d-4c8a-9e1f-0a2b3c4d5e6f", condition_id=str(condition.id)
    )

    effect = assess.originate()

    assert effect is not None


# --- condition ownership on edit ------------------------------------------


def test_edit_accepts_condition_belonging_to_the_commands_patient(
    command: Command, condition: Condition
) -> None:
    """Editing resolves the patient through the command when no note_uuid is set."""
    effect = AssessCommand(command_uuid=str(command.id), condition_id=str(condition.id)).edit()

    assert effect is not None


def test_edit_rejects_condition_belonging_to_another_patient(
    command: Command, foreign_condition: Condition
) -> None:
    """Editing a command to point at another patient's condition is rejected."""
    assess = AssessCommand(command_uuid=str(command.id), condition_id=str(foreign_condition.id))

    with pytest.raises(ValidationError, match="does not belong to this command's patient"):
        assess.edit()


def test_edit_allows_condition_when_command_is_not_yet_persisted(condition: Condition) -> None:
    """A not-yet-persisted command doesn't cause its condition to be rejected."""
    assess = AssessCommand(
        command_uuid="3f7c1a9e-2b6d-4c8a-9e1f-0a2b3c4d5e6f", condition_id=str(condition.id)
    )

    effect = assess.edit()

    assert effect is not None


# --- methods that don't write condition_id --------------------------------


@pytest.mark.parametrize("method", ["commit", "delete", "enter_in_error"])
def test_methods_that_do_not_send_values_skip_the_ownership_check(
    command: Command, foreign_condition: Condition, method: str
) -> None:
    """commit/delete/enter_in_error act on an existing command, so they skip validation."""
    assess = AssessCommand(command_uuid=str(command.id), condition_id=str(foreign_condition.id))

    assert getattr(assess, method)() is not None


# --- condition ownership with no note or command anchor -------------------


def test_originate_without_an_anchor_skips_the_ownership_check(condition: Condition) -> None:
    """Without a note or command to resolve the patient from, ownership can't be checked.

    The command still fails on the required note_uuid, but the cross-patient condition
    error is never raised.
    """
    assess = AssessCommand(condition_id=str(condition.id))

    with pytest.raises(ValidationError, match="note_uuid") as exc_info:
        assess.originate()

    assert "does not belong to this command's patient" not in str(exc_info.value)
