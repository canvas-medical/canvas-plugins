import datetime

import pytest

from canvas_sdk.test_utils.factories import (
    InpatientFacilityFactory,
    InpatientStayFactory,
    NoteFactory,
    PatientFactory,
)
from canvas_sdk.v1.data import InpatientStay, Note


@pytest.mark.django_db
def test_inpatient_stay_reads_its_patient_facility_and_times() -> None:
    """A stay is found by patient and reads its facility, room and admit time."""
    patient = PatientFactory.create()
    facility = InpatientFacilityFactory.create(name="General Hospital", npi_number="1234567893")
    admitted = datetime.datetime(2026, 11, 1, 8, 30, tzinfo=datetime.UTC)
    stay = InpatientStayFactory.create(
        patient=patient, inpatient_facility=facility, room_number="4B", admit_time=admitted
    )

    fetched = InpatientStay.objects.get(patient=patient)

    assert fetched.id == stay.id
    assert fetched.inpatient_facility is not None
    assert fetched.inpatient_facility.name == "General Hospital"
    assert fetched.inpatient_facility.npi_number == "1234567893"
    assert fetched.room_number == "4B"
    assert fetched.admit_time == admitted
    assert fetched.discharge_time is None
    assert list(patient.inpatient_stays.all()) == [fetched]
    assert list(facility.inpatient_stays.all()) == [fetched]


@pytest.mark.django_db
def test_inpatient_stay_allows_no_facility() -> None:
    """A stay recorded without a facility reads it as None."""
    stay = InpatientStayFactory.create(inpatient_facility=None)

    assert InpatientStay.objects.get(id=stay.id).inpatient_facility is None


@pytest.mark.django_db
def test_note_reads_its_inpatient_stay_and_stay_reads_its_rounding_notes() -> None:
    """A rounding note resolves its stay, and the stay lists the note as a rounding note."""
    stay = InpatientStayFactory.create()
    note = NoteFactory.create(patient=stay.patient, inpatient_stay=stay)
    NoteFactory.create(patient=stay.patient)

    assert Note.objects.filter(id=note.id).get().inpatient_stay == stay
    assert list(stay.rounding_notes.all()) == [note]
