import datetime

import pytest
from pydantic_core import ValidationError

from canvas_sdk.commands.commands.close_goal import CloseGoalCommand
from canvas_sdk.test_utils.factories import NoteFactory, PatientFactory
from canvas_sdk.v1.data import Command, Goal, Note, Patient


@pytest.fixture
def patient(db: None) -> Patient:
    """The patient whose chart the command writes to."""
    return PatientFactory.create()


@pytest.fixture
def other_patient(db: None) -> Patient:
    """An unrelated patient, for building a goal that belongs to someone else."""
    return PatientFactory.create()


@pytest.fixture
def note(patient: Patient) -> Note:
    """A note on the target patient's chart."""
    return NoteFactory.create(patient=patient)


def _goal(patient: Patient, note: Note) -> Goal:
    """A goal on a patient's chart."""
    return Goal.objects.create(
        patient=patient,
        note=note,
        goal_statement="Walk 20 minutes daily",
        start_date=datetime.date(2024, 1, 1),
        due_date=datetime.date(2024, 6, 1),
        achievement_status="in-progress",
        priority="medium-priority",
        lifecycle_status="active",
        committer_id=1,
        entered_in_error_id=None,
        deleted=False,
    )


@pytest.fixture
def stored_command(note: Note) -> Command:
    """A persisted closeGoal command on the note, for exercising the edit path."""
    return Command.objects.create(
        note=note,
        patient=note.patient,
        state="staged",
        schema_key="closeGoal",
        data={},
        origination_source="plugin",
        anchor_object_type="",
        anchor_object_dbid=0,
    )


# `goal_id` is a database id, and nothing else refuses one belonging to another patient: the id is
# resolved against the patient downstream and quietly dropped when nothing matches, so a wrong id
# would otherwise produce a close-goal command with no goal on it.


def test_a_goal_on_the_patients_chart_is_accepted(note: Note, patient: Patient) -> None:
    """The ordinary case: the id names one of this patient's goals."""
    goal = _goal(patient, note)

    assert CloseGoalCommand(note_uuid=str(note.id), goal_id=goal.dbid).originate()


def test_a_goal_belonging_to_another_patient_is_refused(note: Note, other_patient: Patient) -> None:
    """The check this exists for — a real goal, but not this patient's."""
    foreign = _goal(other_patient, note)

    with pytest.raises(ValidationError) as caught:
        CloseGoalCommand(note_uuid=str(note.id), goal_id=foreign.dbid).originate()

    assert "not found or not associated with the patient" in str(caught.value)


def test_a_goal_id_that_names_nothing_is_refused(note: Note) -> None:
    """A database id no goal has."""
    with pytest.raises(ValidationError):
        CloseGoalCommand(note_uuid=str(note.id), goal_id=999_999).originate()


def test_the_check_holds_on_an_edit_which_carries_no_note(
    stored_command: Command, note: Note, other_patient: Patient
) -> None:
    """An edit addresses a command rather than a note, and the patient resolves from it."""
    foreign = _goal(other_patient, note)

    with pytest.raises(ValidationError):
        CloseGoalCommand(command_uuid=str(stored_command.id), goal_id=foreign.dbid).edit()


def test_an_edit_naming_the_patients_own_goal_is_allowed(
    stored_command: Command, note: Note, patient: Patient
) -> None:
    """The other half: resolving the patient from the command must not refuse a valid edit."""
    goal = _goal(patient, note)

    assert CloseGoalCommand(command_uuid=str(stored_command.id), goal_id=goal.dbid).edit()


def test_no_goal_id_means_nothing_to_check(note: Note) -> None:
    """The field is optional until commit, so an empty command originates fine."""
    assert CloseGoalCommand(note_uuid=str(note.id)).originate()


def test_a_command_with_neither_anchor_is_not_refused() -> None:
    """A command that cannot know its patient must not guess.

    A plugin can return several effects from one handler, and the note or command a later effect
    names may not be persisted when that effect is built. Asserted with no database available, so a
    lookup would raise rather than return — this passing is the evidence that none happens.
    """
    assert CloseGoalCommand(goal_id=1)._anchor_patient_id() is None


def test_an_uncommitted_goal_is_still_accepted(note: Note, patient: Patient) -> None:
    """Only ownership is checked, so a goal that has not been committed yet is not refused here."""
    goal = _goal(patient, note)
    Goal.objects.filter(dbid=goal.dbid).update(committer_id=None)

    assert CloseGoalCommand(note_uuid=str(note.id), goal_id=goal.dbid).originate()
