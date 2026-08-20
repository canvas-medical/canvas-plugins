from uuid import uuid4

import pytest
from pydantic_core import ValidationError

from canvas_sdk.commands.commands.review.lab import LabReviewCommand
from canvas_sdk.test_utils.factories import LabReportFactory, NoteFactory, PatientFactory
from canvas_sdk.v1.data import Command, LabReport, Note, Patient
from canvas_sdk.v1.data.common import DocumentReviewMode


@pytest.fixture
def patient(db: None) -> Patient:
    """The patient whose chart the command writes to."""
    return PatientFactory.create()


@pytest.fixture
def other_patient(db: None) -> Patient:
    """An unrelated patient, for building a report that belongs to someone else."""
    return PatientFactory.create()


@pytest.fixture
def note(patient: Patient) -> Note:
    """A note on the target patient's chart."""
    return NoteFactory.create(patient=patient)


@pytest.fixture
def report(patient: Patient) -> LabReport:
    """A reviewable lab report on the target patient's chart."""
    return LabReportFactory.create(patient=patient)


@pytest.fixture
def foreign_report(other_patient: Patient) -> LabReport:
    """A reviewable lab report belonging to a different patient."""
    return LabReportFactory.create(patient=other_patient)


@pytest.fixture
def command(note: Note) -> Command:
    """A persisted labReview command on the note, for exercising the edit path."""
    return Command.objects.create(
        note=note,
        patient=note.patient,
        state="staged",
        schema_key="labReview",
        data={},
        origination_source="plugin",
        anchor_object_type="",
        anchor_object_dbid=0,
    )


# --- report ownership -----------------------------------------------------


def test_a_report_on_the_patients_chart_is_accepted(note: Note, report: LabReport) -> None:
    """The ordinary case: the id names one of this patient's reviewable reports."""
    command = LabReviewCommand(note_uuid=str(note.id), report_ids=[str(report.id)])

    assert command.originate()


def test_a_report_belonging_to_another_patient_is_refused(
    note: Note, foreign_report: LabReport
) -> None:
    """The check this exists for — a reviewable report, but not this patient's."""
    command = LabReviewCommand(note_uuid=str(note.id), report_ids=[str(foreign_report.id)])

    with pytest.raises(ValidationError) as caught:
        command.originate()

    assert "does not belong to this command's patient" in str(caught.value)
    assert "LabReport" in str(caught.value)


def test_one_foreign_report_among_several_is_refused(
    note: Note, report: LabReport, foreign_report: LabReport
) -> None:
    """Every id is checked, not just the first."""
    command = LabReviewCommand(
        note_uuid=str(note.id), report_ids=[str(report.id), str(foreign_report.id)]
    )

    with pytest.raises(ValidationError):
        command.originate()


def test_the_check_holds_on_an_edit_which_carries_no_note(
    command: Command, foreign_report: LabReport
) -> None:
    """An edit addresses a command rather than a note, and the patient resolves from it."""
    edit = LabReviewCommand(command_uuid=str(command.id), report_ids=[str(foreign_report.id)])

    with pytest.raises(ValidationError):
        edit.edit()


def test_an_edit_naming_the_patients_own_report_is_allowed(
    command: Command, report: LabReport
) -> None:
    """The other half: resolving the patient from the command must not refuse a valid edit."""
    edit = LabReviewCommand(command_uuid=str(command.id), report_ids=[str(report.id)])

    assert edit.edit()


def test_an_unresolved_anchor_skips_the_ownership_check(foreign_report: LabReport) -> None:
    """No persisted anchor means no patient to check, so ownership is skipped and the report still originates."""
    command = LabReviewCommand(note_uuid=str(uuid4()), report_ids=[str(foreign_report.id)])

    assert command._anchor_patient_id() is None
    assert command.originate()


def test_a_report_that_does_not_need_review_is_still_refused(note: Note, patient: Patient) -> None:
    """Reviewability is still checked alongside ownership, not replaced by it."""
    not_required = LabReportFactory.create(
        patient=patient, review_mode=DocumentReviewMode.REVIEW_NOT_REQUIRED
    )
    command = LabReviewCommand(note_uuid=str(note.id), report_ids=[str(not_required.id)])

    with pytest.raises(ValidationError):
        command.originate()


def test_no_report_ids_means_nothing_to_check(note: Note) -> None:
    """The field is optional until commit, so an empty command originates fine."""
    assert LabReviewCommand(note_uuid=str(note.id)).originate()
