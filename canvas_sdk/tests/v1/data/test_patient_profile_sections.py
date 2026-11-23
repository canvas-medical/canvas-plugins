import pytest

from canvas_sdk.test_utils.factories import (
    PatientFactory,
    PatientKnownLocationFactory,
    PatientParentGuardianFactory,
    PatientTribalAffiliationCodingFactory,
)
from canvas_sdk.v1.data import (
    Patient,
    PatientKnownLocation,
    PatientParentGuardian,
    PatientTribalAffiliationCoding,
)


@pytest.mark.django_db
def test_patient_known_locations_are_read_through_the_patient() -> None:
    """A patient lists its known locations."""
    patient = PatientFactory.create()
    location = PatientKnownLocationFactory.create(patient=patient, known_location="Shelter on 5th")
    PatientKnownLocationFactory.create()

    fetched = PatientKnownLocation.objects.get(patient=patient)

    assert fetched.id == location.id
    assert fetched.known_location == "Shelter on 5th"
    assert list(patient.known_locations.all()) == [fetched]


@pytest.mark.django_db
def test_patient_parent_guardian_is_one_per_patient() -> None:
    """A patient reads its single parent or guardian through ``parent_guardian``."""
    patient = PatientFactory.create()
    guardian = PatientParentGuardianFactory.create(
        patient=patient, first_name="Ana", phone_number="5551234567", state_code="CA"
    )
    PatientParentGuardianFactory.create()

    fetched = PatientParentGuardian.objects.get(patient=patient)

    assert fetched.id == guardian.id
    assert fetched.phone_number == "5551234567"
    assert fetched.state_code == "CA"
    assert Patient.objects.get(dbid=patient.dbid).parent_guardian == fetched


@pytest.mark.django_db
def test_patient_tribal_affiliation_codings_are_read_through_the_patient() -> None:
    """A patient lists its tribal affiliation codings."""
    patient = PatientFactory.create()
    coding = PatientTribalAffiliationCodingFactory.create(patient=patient)
    PatientTribalAffiliationCodingFactory.create()

    fetched = PatientTribalAffiliationCoding.objects.get(patient=patient)

    assert fetched.dbid == coding.dbid
    assert fetched.system == "http://terminology.hl7.org/CodeSystem/v3-TribalEntityUS"
    assert list(patient.tribal_affiliation_coding.all()) == [fetched]
