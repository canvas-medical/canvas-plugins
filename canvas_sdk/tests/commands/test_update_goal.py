import datetime
import uuid

import pytest
from pydantic_core import ValidationError

from canvas_sdk.commands.commands.update_goal import UpdateGoalCommand
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
        schema_key="updateGoal",
        data={},
        origination_source="plugin",
        anchor_object_type="",
        anchor_object_dbid=0,
    )


# `goal_id` is the goal's external id, and nothing else refuses one belonging to another patient. A
# goal named by id is applied as given, and the values the command leaves out are then filled in from
# it — so a foreign id copies that goal's due date and priority onto this patient's note. These assert
# the only check standing in the way.


def test_a_goal_on_the_patients_chart_is_accepted(note: Note, patient: Patient) -> None:
    """The ordinary case: the id names one of this patient's goals."""
    goal = _goal(patient, note)

    assert UpdateGoalCommand(note_uuid=str(note.id), goal_id=goal.id).originate()


def test_a_goal_belonging_to_another_patient_is_refused(note: Note, other_patient: Patient) -> None:
    """The check this exists for — a real goal, but not this patient's."""
    foreign = _goal(other_patient, note)

    with pytest.raises(ValidationError) as caught:
        UpdateGoalCommand(note_uuid=str(note.id), goal_id=foreign.id).originate()

    assert "not found or not associated with the patient" in str(caught.value)


def test_a_goal_id_that_names_nothing_is_refused(note: Note) -> None:
    """A well-formed id no goal has."""
    with pytest.raises(ValidationError):
        UpdateGoalCommand(note_uuid=str(note.id), goal_id=uuid.uuid4()).originate()


def test_a_goal_id_that_cannot_be_an_id_is_a_validation_error(note: Note) -> None:
    """`goal_id` is a UUID, so a malformed value is refused by the field.

    It matters that this is the field's error rather than the database's: filtering an id column with
    an unparseable value raises an error the plugin cannot catch, so the caller would see a server
    error instead of a refusal.
    """
    with pytest.raises(ValidationError):
        UpdateGoalCommand(note_uuid=str(note.id), goal_id="not-a-uuid")  # type: ignore[arg-type]


def test_a_goal_id_given_as_a_string_is_still_accepted(note: Note, patient: Patient) -> None:
    """Callers pass ids as strings, and lenient parsing is what keeps that working.

    The field is typed UUID, so this is the case that breaks if strict parsing ever returns.
    """
    goal = _goal(patient, note)

    command = UpdateGoalCommand(
        note_uuid=str(note.id),
        goal_id=str(goal.id),  # type: ignore[arg-type]
    )

    assert command.originate()


def test_the_check_holds_on_an_edit_which_carries_no_note(
    stored_command: Command, note: Note, other_patient: Patient
) -> None:
    """An edit addresses a command rather than a note, and the patient resolves from it."""
    foreign = _goal(other_patient, note)

    with pytest.raises(ValidationError):
        UpdateGoalCommand(command_uuid=str(stored_command.id), goal_id=foreign.id).edit()


def test_an_edit_naming_the_patients_own_goal_is_allowed(
    stored_command: Command, note: Note, patient: Patient
) -> None:
    """The other half: resolving the patient from the command must not refuse a valid edit."""
    goal = _goal(patient, note)

    assert UpdateGoalCommand(command_uuid=str(stored_command.id), goal_id=goal.id).edit()


def test_no_goal_id_means_nothing_to_check(note: Note) -> None:
    """The field is optional until commit, so an empty command originates fine."""
    assert UpdateGoalCommand(note_uuid=str(note.id)).originate()


def test_a_foreign_goals_data_cannot_be_copied_onto_this_patients_note(
    note: Note, other_patient: Patient
) -> None:
    """The consequence that makes this command's gap worse than close-goal's.

    `payload_values` fills `due_date` and `priority` from the goal when the caller omits them, so an
    unchecked foreign id does not merely point somewhere wrong — it carries another patient's data
    across. Refusing the id is what prevents that.
    """
    foreign = _goal(other_patient, note)

    with pytest.raises(ValidationError):
        UpdateGoalCommand(note_uuid=str(note.id), goal_id=foreign.id, progress="better").originate()


def test_a_goal_is_not_checked_until_the_notes_patient_can_be_resolved(
    note: Note, other_patient: Patient
) -> None:
    """Ownership is checked through validation only once the patient is known.

    A plugin may originate a note and update a goal in the same batch, so the note a
    command names need not be persisted when the effect is built. Until it is,
    `_get_error_details` has no patient to compare against, so it skips the check rather
    than guessing, and even a foreign goal is allowed through here.
    """
    foreign = _goal(other_patient, note)

    command = UpdateGoalCommand(
        note_uuid="3f7c1a9e-2b6d-4c8a-9e1f-0a2b3c4d5e6f",  # a well-formed id no note has
        goal_id=foreign.id,
    )

    assert command.originate()
