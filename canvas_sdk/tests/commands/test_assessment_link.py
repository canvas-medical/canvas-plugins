from uuid import UUID

import pytest
from pydantic_core import ValidationError

from canvas_sdk.commands import (
    CloseGoalCommand,
    FollowUpCommand,
    GoalCommand,
    ImmunizeCommand,
    InstructCommand,
    PerformCommand,
    PlanCommand,
    StopMedicationCommand,
    TaskCommand,
    UpdateGoalCommand,
)
from canvas_sdk.commands.base import _BaseCommand
from canvas_sdk.test_utils.factories import NoteFactory, PatientFactory
from canvas_sdk.v1.data import Assessment, Command, Note, Patient

#: An id no assessment has.
UNKNOWN_ASSESSMENT_ID = UUID("1e2a3b4c-5d6e-4f70-8192-a3b4c5d6e7f8")

ASSESSMENT_LINKED_COMMANDS = (
    CloseGoalCommand,
    FollowUpCommand,
    GoalCommand,
    ImmunizeCommand,
    InstructCommand,
    PerformCommand,
    PlanCommand,
    StopMedicationCommand,
    TaskCommand,
    UpdateGoalCommand,
)


@pytest.fixture
def patient(db: None) -> Patient:
    """The patient whose chart the commands write to."""
    return PatientFactory.create()


@pytest.fixture
def note(patient: Patient) -> Note:
    """A note on the patient's chart."""
    return NoteFactory.create(patient=patient)


@pytest.fixture
def other_note(patient: Patient) -> Note:
    """A second note on the same chart, for building an assessment the command may not link to."""
    return NoteFactory.create(patient=patient)


@pytest.fixture
def stored_command(note: Note) -> Command:
    """A persisted command on the note, for exercising the edit path."""
    return Command.objects.create(
        note=note,
        patient=note.patient,
        state="staged",
        schema_key="instruct",
        data={},
        origination_source="plugin",
        anchor_object_type="",
        anchor_object_dbid=0,
    )


def _assessment(patient: Patient, note: Note) -> Assessment:
    """An assessment made in the given note."""
    return Assessment.objects.create(
        patient=patient,
        note=note,
        status="stable",
        narrative="Stable on current regimen.",
        background="",
        care_team="",
    )


@pytest.mark.parametrize(
    argnames="command_class",
    argvalues=ASSESSMENT_LINKED_COMMANDS,
    ids=[command.__name__ for command in ASSESSMENT_LINKED_COMMANDS],
)
def test_every_in_scope_command_takes_an_assessment(command_class: type[_BaseCommand]) -> None:
    """The field is on each Plan- and Procedures-section command, under the same name."""
    assert "assessment_id" in command_class.model_fields
    assert command_class.command_schema()["assessment"]["required"] is False


def test_an_assessment_made_in_the_same_note_is_accepted(patient: Patient, note: Note) -> None:
    """The ordinary case: the command and the assessment it addresses share a note."""
    assessment = _assessment(patient, note)

    assert InstructCommand(note_uuid=str(note.id), assessment_id=assessment.id).originate()


def test_an_assessment_made_in_another_note_is_refused(
    patient: Patient, note: Note, other_note: Note
) -> None:
    """The check this exists for — a real assessment on the same chart, but not in this note."""
    foreign = _assessment(patient, other_note)

    with pytest.raises(ValidationError) as caught:
        InstructCommand(note_uuid=str(note.id), assessment_id=foreign.id).originate()

    assert "was not made in this command's note" in str(caught.value)


def test_an_assessment_id_that_names_nothing_is_refused(note: Note) -> None:
    """An id no assessment has."""
    with pytest.raises(ValidationError):
        InstructCommand(note_uuid=str(note.id), assessment_id=UNKNOWN_ASSESSMENT_ID).originate()


def test_no_assessment_means_nothing_to_check(note: Note) -> None:
    """The link is optional, so a command committed without one is valid."""
    assert InstructCommand(note_uuid=str(note.id), comment="Rest and fluids").originate()


def test_the_check_holds_on_an_edit_which_carries_no_note(
    patient: Patient, stored_command: Command, other_note: Note
) -> None:
    """An edit addresses a command rather than a note, and the note resolves from it."""
    foreign = _assessment(patient, other_note)

    with pytest.raises(ValidationError):
        InstructCommand(command_uuid=str(stored_command.id), assessment_id=foreign.id).edit()


def test_an_edit_naming_an_assessment_in_the_commands_own_note_is_allowed(
    patient: Patient, stored_command: Command, note: Note
) -> None:
    """The other half: resolving the note from the command must not refuse a valid edit."""
    assessment = _assessment(patient, note)

    assert InstructCommand(command_uuid=str(stored_command.id), assessment_id=assessment.id).edit()


def test_a_command_with_neither_anchor_is_not_refused() -> None:
    """A command that cannot know its note must not guess.

    A plugin can return several effects from one handler, and the note or command a later effect
    names may not be persisted when that effect is built. Asserted with no database available, so a
    lookup would raise rather than return — this passing is the evidence that none happens.
    """
    command = InstructCommand(assessment_id=UNKNOWN_ASSESSMENT_ID)

    assert command._anchor_note_id() is None


def test_the_link_travels_in_the_effect_payload(patient: Patient, note: Note) -> None:
    """The interpreter reads `assessment_id`, so that is the name the effect has to carry."""
    assessment = _assessment(patient, note)

    effect = InstructCommand(note_uuid=str(note.id), assessment_id=assessment.id).originate()

    assert f'"assessment_id": "{assessment.id}"' in effect.payload
