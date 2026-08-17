import datetime
from uuid import uuid4

import pytest
from pydantic_core import ValidationError

from canvas_sdk.commands import RemoveAllergyCommand
from canvas_sdk.test_utils.factories import NoteFactory, PatientFactory
from canvas_sdk.v1.data import AllergyIntolerance, Command, Note, Patient

NOTE_UUID = "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"


@pytest.fixture
def patient(db: None) -> Patient:
    """A patient who owns the note the command is charted in."""
    return PatientFactory.create()


@pytest.fixture
def other_patient(db: None) -> Patient:
    """An unrelated patient, used to build a cross-patient allergy."""
    return PatientFactory.create()


@pytest.fixture
def note(patient: Patient) -> Note:
    """A note belonging to `patient`."""
    return NoteFactory.create(patient=patient)


def _allergy(patient: Patient, status: str = "active") -> AllergyIntolerance:
    """Create a minimal allergy for the given patient."""
    return AllergyIntolerance.objects.create(
        patient=patient,
        deleted=False,
        note_id=0,
        allergy_intolerance_type="A",
        category=1,
        status=status,
        severity="moderate",
        onset_date=datetime.date(2024, 1, 1),
        onset_date_original_input="",
        last_occurrence=datetime.date(2024, 1, 1),
        last_occurrence_original_input="",
        recorded_date=datetime.datetime(2024, 1, 1, tzinfo=datetime.UTC),
        narrative="",
    )


@pytest.fixture
def allergy(patient: Patient) -> AllergyIntolerance:
    """An allergy belonging to the same patient as the note."""
    return _allergy(patient)


@pytest.fixture
def foreign_allergy(other_patient: Patient) -> AllergyIntolerance:
    """An allergy belonging to a different patient than the note."""
    return _allergy(other_patient)


@pytest.fixture
def command(note: Note) -> Command:
    """A persisted removeAllergy command anchored to `note`, for exercising edit()."""
    return Command.objects.create(
        note=note,
        patient=note.patient,
        state="staged",
        schema_key="removeAllergy",
        data={},
        origination_source="plugin",
        anchor_object_type="",
        anchor_object_dbid=0,
    )


# --- allergy ownership on originate ---------------------------------------


def test_originate_accepts_allergy_belonging_to_the_notes_patient(
    note: Note, allergy: AllergyIntolerance
) -> None:
    """The ordinary case: the id names one of this patient's allergies."""
    command = RemoveAllergyCommand(note_uuid=str(note.id), allergy_id=allergy.id)

    assert command.originate()


def test_originate_rejects_allergy_belonging_to_another_patient(
    note: Note, foreign_allergy: AllergyIntolerance
) -> None:
    """A real allergy, but not this patient's.

    Without this the command was charted with no allergy at all, because the id is resolved against
    the patient downstream and quietly dropped when nothing matches.
    """
    command = RemoveAllergyCommand(note_uuid=str(note.id), allergy_id=foreign_allergy.id)

    with pytest.raises(ValidationError) as caught:
        command.originate()

    assert "does not belong to this command's patient" in str(caught.value)


def test_originate_rejects_an_unknown_allergy(note: Note) -> None:
    """A well-formed id that names nothing."""
    command = RemoveAllergyCommand(note_uuid=str(note.id), allergy_id=uuid4())

    with pytest.raises(ValidationError):
        command.originate()


# --- allergy ownership on edit --------------------------------------------


def test_edit_accepts_allergy_belonging_to_the_commands_patient(
    command: Command, allergy: AllergyIntolerance
) -> None:
    """An edit names a command rather than a note, and the patient resolves from it."""
    edit = RemoveAllergyCommand(command_uuid=str(command.id), allergy_id=allergy.id)

    assert edit.edit()


def test_edit_rejects_allergy_belonging_to_another_patient(
    command: Command, foreign_allergy: AllergyIntolerance
) -> None:
    """The other half: an edit cannot point at another patient's allergy."""
    edit = RemoveAllergyCommand(command_uuid=str(command.id), allergy_id=foreign_allergy.id)

    with pytest.raises(ValidationError):
        edit.edit()


# --- cases with nothing to check ------------------------------------------


def test_no_allergy_id_means_nothing_to_check(note: Note) -> None:
    """The field is optional until commit, so an empty command originates fine."""
    assert RemoveAllergyCommand(note_uuid=str(note.id)).originate()


def test_an_id_that_cannot_be_an_id_is_a_validation_error(note: Note) -> None:
    """`allergy_id` is a UUID, so a malformed value is refused by the field.

    It matters that this is the field's error rather than the database's: filtering an id column with
    an unparseable value raises an error the plugin cannot catch, so the caller would see a server
    error instead of a refusal.
    """
    with pytest.raises(ValidationError):
        RemoveAllergyCommand(note_uuid=str(note.id), allergy_id="99999")  # type: ignore[arg-type]


def test_an_id_given_as_a_string_is_still_accepted(note: Note, allergy: AllergyIntolerance) -> None:
    """Callers pass ids as strings, and lenient parsing is what keeps that working.

    The field is typed UUID, so this is the case that breaks if strict parsing ever returns.
    """
    command = RemoveAllergyCommand(
        note_uuid=str(note.id),
        allergy_id=str(allergy.id),  # type: ignore[arg-type]
    )

    assert command.originate()


def test_a_command_with_neither_anchor_skips_the_check(allergy: AllergyIntolerance) -> None:
    """A command that cannot know its patient must not guess."""
    command = RemoveAllergyCommand(allergy_id=allergy.id)

    assert command._anchor_patient_id() is None


# --- narrative max length -------------------------------------------------


def test_narrative_accepts_max_length() -> None:
    """Narrative accepts a value at the 512 character limit."""
    text = "a" * 512

    assert RemoveAllergyCommand(note_uuid=NOTE_UUID, narrative=text).narrative == text


def test_narrative_rejects_above_max_length() -> None:
    """Over the limit is refused, against the field, so a caller knows what to shorten."""
    with pytest.raises(ValidationError) as caught:
        RemoveAllergyCommand(note_uuid=NOTE_UUID, narrative="a" * 513)

    error = caught.value.errors()[0]
    assert error["loc"] == ("narrative",)
    assert error["type"] == "string_too_long"


def test_narrative_rejects_above_max_length_on_assignment() -> None:
    """The narrative is validated when assigned after construction."""
    command = RemoveAllergyCommand(note_uuid=NOTE_UUID)

    with pytest.raises(ValidationError):
        command.narrative = "a" * 513
