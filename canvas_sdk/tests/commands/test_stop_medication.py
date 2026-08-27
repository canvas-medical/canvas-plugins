from uuid import uuid4

import pytest
from pydantic_core import ValidationError

from canvas_sdk.commands import StopMedicationCommand
from canvas_sdk.test_utils.factories import MedicationFactory, NoteFactory, PatientFactory
from canvas_sdk.v1.data import Command, Medication, Note, Patient
from canvas_sdk.v1.data.medication import Status


@pytest.fixture
def patient(db: None) -> Patient:
    """A patient who owns the note the command is charted in."""
    return PatientFactory.create()


@pytest.fixture
def other_patient(db: None) -> Patient:
    """An unrelated patient, used to build a cross-patient medication."""
    return PatientFactory.create()


@pytest.fixture
def note(patient: Patient) -> Note:
    """A note belonging to `patient`."""
    return NoteFactory.create(patient=patient)


@pytest.fixture
def medication(patient: Patient) -> Medication:
    """A medication belonging to the same patient as the note."""
    return MedicationFactory.create(patient=patient)


@pytest.fixture
def foreign_medication(other_patient: Patient) -> Medication:
    """A medication belonging to a different patient than the note."""
    return MedicationFactory.create(patient=other_patient)


@pytest.fixture
def command(note: Note) -> Command:
    """A persisted stopMedication command anchored to `note`, for exercising edit()."""
    return Command.objects.create(
        note=note,
        patient=note.patient,
        state="staged",
        schema_key="stopMedication",
        data={},
        origination_source="plugin",
        anchor_object_type="",
        anchor_object_dbid=0,
    )


# --- medication ownership on originate ------------------------------------


def test_originate_accepts_medication_belonging_to_the_notes_patient(
    note: Note, medication: Medication
) -> None:
    """The ordinary case: the id names one of this patient's medications."""
    command = StopMedicationCommand(note_uuid=str(note.id), medication_id=medication.id)

    assert command.originate()


def test_originate_rejects_medication_belonging_to_another_patient(
    note: Note, foreign_medication: Medication
) -> None:
    """A real medication, but not this patient's.

    Without this the command was charted with no medication at all, because the id was resolved
    against the patient and quietly dropped when nothing matched.
    """
    command = StopMedicationCommand(note_uuid=str(note.id), medication_id=foreign_medication.id)

    with pytest.raises(ValidationError) as caught:
        command.originate()

    assert "does not belong to this command's patient" in str(caught.value)


def test_originate_rejects_an_unknown_medication(note: Note) -> None:
    """A well-formed id that names nothing."""
    command = StopMedicationCommand(note_uuid=str(note.id), medication_id=uuid4())

    with pytest.raises(ValidationError):
        command.originate()


def test_an_inactive_medication_is_still_accepted(note: Note, patient: Patient) -> None:
    """Only ownership is checked, not the medication's status.

    A medication the patient has should not be refused here on the basis of its status; the check
    stays at what the record itself requires.
    """
    inactive = MedicationFactory.create(patient=patient, status=Status.INACTIVE)
    command = StopMedicationCommand(note_uuid=str(note.id), medication_id=inactive.id)

    assert command.originate()


# --- medication ownership on edit -----------------------------------------


def test_edit_accepts_medication_belonging_to_the_commands_patient(
    command: Command, medication: Medication
) -> None:
    """An edit names a command rather than a note, and the patient resolves from it."""
    edit = StopMedicationCommand(command_uuid=str(command.id), medication_id=medication.id)

    assert edit.edit()


def test_edit_rejects_medication_belonging_to_another_patient(
    command: Command, foreign_medication: Medication
) -> None:
    """The other half: an edit cannot point at another patient's medication."""
    edit = StopMedicationCommand(command_uuid=str(command.id), medication_id=foreign_medication.id)

    with pytest.raises(ValidationError):
        edit.edit()


# --- cases with nothing to check ------------------------------------------


def test_no_medication_id_means_nothing_to_check(note: Note) -> None:
    """The field is optional until commit, so an empty command originates fine."""
    assert StopMedicationCommand(note_uuid=str(note.id)).originate()
