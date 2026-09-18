import datetime
import json
from uuid import uuid4

import pytest
from pydantic_core import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.commands import RemovePastMedicalHistoryCommand
from canvas_sdk.test_utils.factories import NoteFactory, PatientFactory
from canvas_sdk.v1.data import Command, Condition, Note, Patient


@pytest.fixture
def patient(db: None) -> Patient:
    """A patient who owns the note the command is charted in."""
    return PatientFactory.create()


@pytest.fixture
def other_patient(db: None) -> Patient:
    """An unrelated patient, used to build a cross-patient entry."""
    return PatientFactory.create()


@pytest.fixture
def note(patient: Patient) -> Note:
    """A note belonging to `patient`."""
    return NoteFactory.create(patient=patient)


def _past_medical_history(
    patient: Patient,
    clinical_status: str = "resolved",
    committer_id: int | None = 1,
    entered_in_error_id: int | None = None,
    surgical: bool = False,
) -> Condition:
    """A past medical history entry on a patient's chart.

    The Past Medical History command anchors to a Condition and originates it with a "resolved"
    clinical status, so that is the shape a real entry has.
    """
    return Condition.objects.create(
        patient=patient,
        deleted=False,
        onset_date=datetime.date(2024, 1, 1),
        resolution_date=datetime.date(2024, 1, 1),
        clinical_status=clinical_status,
        committer_id=committer_id,
        entered_in_error_id=entered_in_error_id,
        notes="",
        surgical=surgical,
    )


@pytest.fixture
def entry(patient: Patient) -> Condition:
    """A past medical history entry belonging to the same patient as the note."""
    return _past_medical_history(patient)


@pytest.fixture
def foreign_entry(other_patient: Patient) -> Condition:
    """A past medical history entry belonging to a different patient than the note."""
    return _past_medical_history(other_patient)


def _anchored(
    command: RemovePastMedicalHistoryCommand, note: Note
) -> RemovePastMedicalHistoryCommand:
    """Attach the note after construction.

    Constructor keys are all marked dirty, while assignment honors the excluded list, so setting
    the anchor here keeps it out of the effect payload.
    """
    command.note_uuid = str(note.id)
    return command


@pytest.fixture
def command(note: Note) -> Command:
    """A persisted removePastMedicalHistory command anchored to `note`, for exercising edit()."""
    return Command.objects.create(
        note=note,
        patient=note.patient,
        state="staged",
        schema_key="removePastMedicalHistory",
        data={},
        origination_source="plugin",
        anchor_object_type="",
        anchor_object_dbid=0,
    )


# --- effect shape ---------------------------------------------------------


def test_constantized_key_matches_the_effect_names() -> None:
    """The effect enum names are derived from the key, so the two have to agree."""
    assert RemovePastMedicalHistoryCommand().constantized_key() == "REMOVE_PAST_MEDICAL_HISTORY"


def test_originate_carries_every_field(note: Note, entry: Condition) -> None:
    """Originating sends both fields, with the target id as a string."""
    command = _anchored(
        RemovePastMedicalHistoryCommand(
            condition_id=entry.id,
            rationale="Imported in error from the HIE feed.",
        ),
        note,
    )

    effect = command.originate()

    assert effect.type == EffectType.ORIGINATE_REMOVE_PAST_MEDICAL_HISTORY_COMMAND
    assert json.loads(effect.payload)["data"] == {
        "condition_id": str(entry.id),
        "rationale": "Imported in error from the HIE feed.",
    }


def test_only_the_fields_that_were_set_are_sent(note: Note, entry: Condition) -> None:
    """Dirty tracking keeps an untouched field out of the payload."""
    command = _anchored(RemovePastMedicalHistoryCommand(condition_id=entry.id), note)

    assert json.loads(command.originate().payload)["data"] == {"condition_id": str(entry.id)}


def test_the_commands_api_renames_the_target_field() -> None:
    """The note's schema calls the field `past_medical_history`, and the API follows it."""
    assert "condition" in RemovePastMedicalHistoryCommand.command_schema()


def test_commit_needs_only_the_command_id() -> None:
    """A command staged in the note is committed by id, without restating its fields."""
    effect = RemovePastMedicalHistoryCommand(command_uuid="cmd-456").commit()

    assert effect.type == EffectType.COMMIT_REMOVE_PAST_MEDICAL_HISTORY_COMMAND


def test_a_rationale_over_the_limit_is_refused() -> None:
    """The note's rationale field stores 512 characters."""
    with pytest.raises(ValidationError):
        RemovePastMedicalHistoryCommand(rationale="a" * 513)


# --- ownership on originate -----------------------------------------------


def test_originate_accepts_an_entry_belonging_to_the_notes_patient(
    note: Note, entry: Condition
) -> None:
    """The ordinary case: the id names one of this patient's past medical history entries.

    A real entry is resolved rather than active, so guarding with `Condition.objects.active()`
    here, as the sibling Resolve Condition command does, would refuse every one of them.
    """
    command = RemovePastMedicalHistoryCommand(note_uuid=str(note.id), condition_id=entry.id)

    assert command.originate()


def test_originate_rejects_an_entry_belonging_to_another_patient(
    note: Note, foreign_entry: Condition
) -> None:
    """A real entry, but not this patient's."""
    command = RemovePastMedicalHistoryCommand(note_uuid=str(note.id), condition_id=foreign_entry.id)

    with pytest.raises(ValidationError) as caught:
        command.originate()

    assert "does not belong to this command's patient" in str(caught.value)


def test_originate_rejects_an_unknown_entry(note: Note) -> None:
    """A well-formed id that names nothing."""
    command = RemovePastMedicalHistoryCommand(note_uuid=str(note.id), condition_id=uuid4())

    with pytest.raises(ValidationError):
        command.originate()


def test_an_uncommitted_entry_is_refused(note: Note, patient: Patient) -> None:
    """A staged entry is not yet on the chart, so there is nothing to remove."""
    uncommitted = _past_medical_history(patient, committer_id=None)

    with pytest.raises(ValidationError):
        RemovePastMedicalHistoryCommand(
            note_uuid=str(note.id), condition_id=uncommitted.id
        ).originate()


def test_an_already_removed_entry_is_refused(note: Note, patient: Patient) -> None:
    """Removing an entry enters its Condition in error, and `committed()` excludes those."""
    already_removed = _past_medical_history(patient, entered_in_error_id=1)

    with pytest.raises(ValidationError):
        RemovePastMedicalHistoryCommand(
            note_uuid=str(note.id), condition_id=already_removed.id
        ).originate()


def test_an_active_condition_is_refused(note: Note, patient: Patient) -> None:
    """An active problem is Resolve Condition's business, not this command's.

    home-app resolves the id against its past-medical-history scope and leaves the field unset
    when nothing matches, so accepting this here would originate a command with no target.
    """
    active = _past_medical_history(patient, clinical_status="active")

    with pytest.raises(ValidationError) as caught:
        RemovePastMedicalHistoryCommand(note_uuid=str(note.id), condition_id=active.id).originate()

    assert "is not a past medical history entry" in str(caught.value)


def test_surgical_history_is_refused(note: Note, patient: Patient) -> None:
    """Past surgical history is a separate command with its own chart section.

    Its entries are committed and resolved too, so the surgical flag is the only thing that
    separates the two populations.
    """
    surgery = _past_medical_history(patient, surgical=True)

    with pytest.raises(ValidationError) as caught:
        RemovePastMedicalHistoryCommand(note_uuid=str(note.id), condition_id=surgery.id).originate()

    assert "is not a past medical history entry" in str(caught.value)


# --- ownership on edit ----------------------------------------------------


def test_edit_accepts_an_entry_belonging_to_the_commands_patient(
    command: Command, entry: Condition
) -> None:
    """An edit names a command rather than a note, and the patient resolves through it."""
    edit = RemovePastMedicalHistoryCommand(command_uuid=str(command.id), condition_id=entry.id)

    assert edit.edit()


def test_edit_rejects_an_entry_belonging_to_another_patient(
    command: Command, foreign_entry: Condition
) -> None:
    """The other half: resolving through the command still refuses a foreign entry."""
    edit = RemovePastMedicalHistoryCommand(
        command_uuid=str(command.id), condition_id=foreign_entry.id
    )

    with pytest.raises(ValidationError):
        edit.edit()


# --- cases with nothing to check ------------------------------------------


def test_no_target_means_nothing_to_check(note: Note) -> None:
    """The field is optional, so an empty command can be dropped into a note and filled in."""
    assert RemovePastMedicalHistoryCommand(note_uuid=str(note.id)).originate()
