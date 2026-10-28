from datetime import UTC, datetime

import pytest

from canvas_sdk.agents import find_open_note_uuid_from_ctx
from canvas_sdk.test_utils.factories import NoteFactory, PatientFactory, StaffFactory
from canvas_sdk.v1.data.note import CurrentNoteStateEvent, Note, NoteStates


def _open_note(**kwargs: object) -> Note:
    """A note in NEW state; the current-state view is a plain table in tests."""
    note = NoteFactory.create(**kwargs)
    CurrentNoteStateEvent.objects.create(note=note, state=NoteStates.NEW)
    return note


@pytest.mark.django_db
def test_open_note_resolver_picks_the_requesting_staffs_note() -> None:
    """A clinician's chat drafts land on their own open note, not a colleague's newer one."""
    patient = PatientFactory.create()
    clinician = StaffFactory.create()
    own_note = _open_note(
        patient=patient, provider=clinician, datetime_of_service=datetime(2026, 1, 1, tzinfo=UTC)
    )
    _open_note(patient=patient, datetime_of_service=datetime(2026, 6, 1, tzinfo=UTC))

    note_id = find_open_note_uuid_from_ctx({"patient_id": patient.id, "staff_id": clinician.id})

    assert note_id == str(own_note.id)


@pytest.mark.django_db
def test_open_note_resolver_finds_nothing_when_only_a_colleague_has_one_open() -> None:
    """With no open note of their own, the tool asks the clinician to open one."""
    patient = PatientFactory.create()
    _open_note(patient=patient)

    note_id = find_open_note_uuid_from_ctx(
        {"patient_id": patient.id, "staff_id": StaffFactory.create().id}
    )

    assert note_id is None


@pytest.mark.django_db
def test_open_note_resolver_without_a_staff_uses_the_patients_newest_open_note() -> None:
    """A triggered agent with no requesting staff still finds the patient's open note."""
    patient = PatientFactory.create()
    _open_note(patient=patient, datetime_of_service=datetime(2026, 1, 1, tzinfo=UTC))
    newest = _open_note(patient=patient, datetime_of_service=datetime(2026, 6, 1, tzinfo=UTC))

    assert find_open_note_uuid_from_ctx({"patient_id": patient.id}) == str(newest.id)
