import pytest

from canvas_sdk.test_utils.factories import (
    CanvasUserFactory,
    ConsolidatedImmunizationCodingFactory,
    ConsolidatedImmunizationFactory,
    ContentTypeFactory,
    NoteFactory,
    PatientFactory,
    StaffFactory,
)
from canvas_sdk.v1.data import ConsolidatedImmunization, ImmunizationStatement
from canvas_sdk.value_set.value_set import ValueSet


class _CovidVaccineValueSet(ValueSet):
    """Tiny value set fixture for find() tests."""

    VALUE_SET_NAME = "COVID vaccine sample"
    OID = "tests.covid-vaccine-sample"
    CVX = {"208"}


@pytest.mark.django_db
def test_consolidated_immunization_is_read_through_its_patient_note_and_staff() -> None:
    """A record is found from its patient, note and administering staff, and reads its fields."""
    patient = PatientFactory.create()
    note = NoteFactory.create(patient=patient)
    staff = StaffFactory.create()
    record = ConsolidatedImmunizationFactory.create(
        patient=patient, note=note, given_by=staff, lot_number="EL9261", primary_source=False
    )
    ConsolidatedImmunizationFactory.create()

    fetched = ConsolidatedImmunization.objects.get(id=record.id)

    assert fetched.lot_number == "EL9261"
    assert fetched.primary_source is False
    assert list(patient.consolidated_immunizations.all()) == [fetched]
    assert list(note.consolidated_immunizations.all()) == [fetched]
    assert list(staff.consolidated_immunizations_given.all()) == [fetched]


@pytest.mark.django_db
def test_consolidated_immunization_codings_resolve_from_the_patient() -> None:
    """A patient's consolidated immunizations filter by the code of their codings."""
    record = ConsolidatedImmunizationFactory.create()
    coding = ConsolidatedImmunizationCodingFactory.create(consolidated_immunization=record)
    ConsolidatedImmunizationCodingFactory.create(code="141")

    assert list(record.coding.all()) == [coding]
    assert list(record.patient.consolidated_immunizations.filter(coding__code="208")) == [record]


@pytest.mark.django_db
def test_consolidated_immunization_find_and_committed() -> None:
    """find() matches a value set through the coding accessor; committed() drops unsigned rows."""
    signed = ConsolidatedImmunizationFactory.create(committer=CanvasUserFactory.create())
    ConsolidatedImmunizationCodingFactory.create(consolidated_immunization=signed)
    unsigned = ConsolidatedImmunizationFactory.create()
    ConsolidatedImmunizationCodingFactory.create(consolidated_immunization=unsigned, code="141")

    assert list(ConsolidatedImmunization.objects.find(_CovidVaccineValueSet)) == [signed]
    assert list(ConsolidatedImmunization.objects.committed()) == [signed]


@pytest.mark.django_db
def test_consolidated_immunization_source_resolves_the_statement_it_was_built_from() -> None:
    """``source`` resolves the content type + object id to the ImmunizationStatement."""
    note = NoteFactory.create()
    statement = ImmunizationStatement.objects.create(patient=note.patient, note=note)
    record = ConsolidatedImmunizationFactory.create(
        patient=note.patient,
        note=note,
        content_type=ContentTypeFactory.create(model="immunizationstatement"),
        object_id=statement.dbid,
    )

    assert record.source == statement


@pytest.mark.django_db
def test_consolidated_immunization_source_is_none_for_an_unmapped_content_type() -> None:
    """A content type with no SDK model resolves to None."""
    record = ConsolidatedImmunizationFactory.create(
        content_type=ContentTypeFactory.create(model="unknown")
    )

    assert record.source is None
