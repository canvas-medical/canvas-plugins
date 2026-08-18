import datetime
import uuid

import pytest
from pydantic_core import ValidationError

from canvas_sdk.commands.commands.change_medication import ChangeMedicationCommand
from canvas_sdk.test_utils.factories import NoteFactory, PatientFactory
from canvas_sdk.v1.data import Command, Medication, Note, Patient


@pytest.fixture
def patient(db: None) -> Patient:
    """The patient whose chart the command writes to."""
    return PatientFactory.create()


@pytest.fixture
def other_patient(db: None) -> Patient:
    """An unrelated patient, for building a medication that belongs to someone else."""
    return PatientFactory.create()


@pytest.fixture
def note(patient: Patient) -> Note:
    """A note on the target patient's chart."""
    return NoteFactory.create(patient=patient)


def _medication(patient: Patient, status: str = "active") -> Medication:
    """A medication on a patient's list, as `Medication.objects.active()` defines one.

    That is `committed()` — a committer, no entered-in-error — plus `status="active"`. The
    interpreter resolves against the same queryset, so a fixture that skipped any of it would
    prove the command accepts medications the interpreter will then fail to find.
    """
    return Medication.objects.create(
        patient=patient,
        deleted=False,
        status=status,
        committer_id=1,
        entered_in_error_id=None,
        start_date=datetime.date(2024, 1, 1),
        end_date=datetime.date(2030, 1, 1),
        national_drug_code="",
        erx_quantity=0,
        quantity_qualifier_description="",
        clinical_quantity_description="",
        potency_unit_code="",
    )


@pytest.fixture
def stored_command(note: Note) -> Command:
    """A persisted changeMedication command on the note, for exercising the edit path."""
    return Command.objects.create(
        note=note,
        patient=note.patient,
        state="staged",
        schema_key="changeMedication",
        data={},
        origination_source="plugin",
        anchor_object_type="",
        anchor_object_dbid=0,
    )


# The medication being changed has to be one the patient actually has. The interpreter resolves
# `medication_id` against the note's patient and stores *no medication* when nothing matches
# (`plugin_io/interpreters/commands/change_medication.py`), so without this the command is created
# with an empty medication instead of reporting the bad id.


def test_a_medication_on_the_patients_list_is_accepted(note: Note, patient: Patient) -> None:
    """The ordinary case: the id names one of this patient's active medications."""
    medication = _medication(patient)

    command = ChangeMedicationCommand(note_uuid=str(note.id), medication_id=medication.id)

    assert command.originate()


def test_a_medication_belonging_to_another_patient_is_refused(
    note: Note, other_patient: Patient
) -> None:
    """The check this exists for — a valid medication, but not this patient's."""
    foreign = _medication(other_patient)

    with pytest.raises(ValidationError) as caught:
        ChangeMedicationCommand(note_uuid=str(note.id), medication_id=foreign.id).originate()

    assert "not found or not associated with the patient" in str(caught.value)


def test_an_unknown_medication_is_refused(note: Note) -> None:
    """A well-formed id that names nothing."""
    with pytest.raises(ValidationError):
        ChangeMedicationCommand(note_uuid=str(note.id), medication_id=uuid.uuid4()).originate()


def test_an_inactive_medication_is_refused(note: Note, patient: Patient) -> None:
    """The interpreter only resolves active medications, so this mirrors what it will accept."""
    inactive = _medication(patient, status="inactive")

    with pytest.raises(ValidationError):
        ChangeMedicationCommand(note_uuid=str(note.id), medication_id=inactive.id).originate()


def test_the_check_holds_on_an_edit_which_carries_no_note(
    stored_command: Command, other_patient: Patient
) -> None:
    """The bug this fixes: an edit addresses a command, not a note.

    Reading only ``note_uuid`` left ``note`` as None on this path, and the ownership check sat
    behind `if self.medication_id and note:` — so editing a command to point at another patient's
    medication was accepted, and the interpreter then quietly stored no medication at all.
    """
    foreign = _medication(other_patient)

    with pytest.raises(ValidationError):
        ChangeMedicationCommand(
            command_uuid=str(stored_command.id), medication_id=foreign.id
        ).edit()


def test_an_edit_naming_the_patients_own_medication_is_allowed(
    stored_command: Command, patient: Patient
) -> None:
    """The other half: resolving the patient from the command must not refuse a valid edit."""
    medication = _medication(patient)

    command = ChangeMedicationCommand(
        command_uuid=str(stored_command.id), medication_id=medication.id
    )

    assert command.edit()


def test_a_medication_id_that_cannot_be_an_id_is_a_validation_error(note: Note) -> None:
    """`medication_id` is a UUID, so pydantic refuses a malformed one.

    It matters that this is pydantic's error and not Django's: filtering an id column with an
    unparseable value raises `django.core.exceptions.ValidationError`, which the plugin sandbox
    cannot catch — so it would reach the caller as a 500 rather than as a refusal.
    """
    with pytest.raises(ValidationError):
        # A string is what a caller actually sends; the annotation says UUID, and pydantic reads a
        # well-formed one leniently — this asserts what happens to one that is not.
        ChangeMedicationCommand(note_uuid=str(note.id), medication_id="99999")  # type: ignore[arg-type]


def test_a_medication_id_given_as_a_string_is_still_accepted(note: Note, patient: Patient) -> None:
    """The field was declared `str` before this change, so its callers pass one.

    Retyping it to UUID only stays compatible because commands parse leniently. Under strict
    parsing pydantic refuses the string form outright — `Input should be an instance of UUID` —
    which would break every plugin that passes the id the way it used to be declared.
    """
    medication = _medication(patient)

    command = ChangeMedicationCommand(
        note_uuid=str(note.id),
        medication_id=str(medication.id),  # type: ignore[arg-type]
    )

    assert command.originate()


def test_no_medication_id_means_nothing_to_check(note: Note) -> None:
    """The field is optional until commit, so an empty command originates fine."""
    assert ChangeMedicationCommand(note_uuid=str(note.id)).originate()


def test_a_command_with_neither_anchor_is_not_refused() -> None:
    """A command that cannot know its patient must not guess.

    A plugin can return several effects from one handler; the note or command a later effect names
    may not be persisted at the moment that effect is built, and refusing then would break a
    legitimate chain. Asserted with no database available, so a lookup would raise rather than
    return — this passing is the evidence that none happens.
    """
    command = ChangeMedicationCommand(medication_id=uuid.uuid4())

    assert command._anchor_patient_id() is None
