"""Tests for test helper functions."""

from typing import Any

import arrow
import pytest

from canvas_sdk.protocols.clinical_quality_measure import ClinicalQualityMeasure
from canvas_sdk.test_utils.factories import PatientFactory
from canvas_sdk.test_utils.helpers import (
    create_condition_with_coding,
    create_encounter_with_billing,
    create_imaging_report_with_coding,
    create_protocol_instance,
)
from canvas_sdk.v1.data.billing import BillingLineItem
from canvas_sdk.v1.data.condition import Condition
from canvas_sdk.v1.data.imaging import ImagingReport
from canvas_sdk.v1.data.note import Note
from canvas_sdk.v1.data.patient import Patient
from canvas_sdk.value_set.value_set import ValueSet


class MockCQM(ClinicalQualityMeasure):
    """Mock Clinical Quality Measure for testing."""

    class Meta:
        title = "Mock CQM"
        description = "Test CQM"
        version = "v1"
        information = "https://example.com"
        identifiers = ["MOCK001"]
        types = ["process"]
        compute_on_change_types: list[str] = []
        references: list[str] = []

    def compute(self) -> list[Any]:
        """Mock compute method - required abstract method."""
        return []

    def compute_results(self) -> dict[str, Any]:
        """Mock compute_results."""
        return {}


class DiabetesValueSet(ValueSet):
    """Mock ValueSet for diabetes conditions."""

    SNOMEDCT = {"73211009", "44054006"}
    ICD10CM = {"E11.9", "E10.9"}


class OfficeVisitValueSet(ValueSet):
    """Mock ValueSet for office visits."""

    CPT = {"99213", "99214"}
    HCPCS = {"G0463"}


class MammographyValueSet(ValueSet):
    """Mock ValueSet for mammography imaging."""

    LOINC = {"24606-6", "24605-8"}
    SNOMEDCT = {"71651007", "241055006"}


@pytest.mark.django_db
def test_create_protocol_instance_default_timeframe() -> None:
    """Test creating a protocol instance with default timeframe."""
    protocol = create_protocol_instance(MockCQM)

    assert isinstance(protocol, MockCQM)
    assert hasattr(protocol, "timeframe")
    assert protocol.timeframe.end <= arrow.now()
    # Timeframe should be approximately 1 year
    diff = protocol.timeframe.end.datetime - protocol.timeframe.start.datetime
    assert 360 <= diff.days <= 370


@pytest.mark.django_db
def test_create_protocol_instance_custom_timeframe() -> None:
    """Test creating a protocol instance with custom timeframe."""
    start = arrow.get("2023-01-01")
    end = arrow.get("2023-12-31")

    protocol = create_protocol_instance(MockCQM, start, end)

    assert protocol.timeframe.start == start
    assert protocol.timeframe.end == end


@pytest.mark.django_db
def test_create_protocol_instance_only_end_date() -> None:
    """Test creating a protocol instance with only end date specified."""
    end = arrow.get("2024-06-30")

    protocol = create_protocol_instance(MockCQM, timeframe_end=end)

    assert protocol.timeframe.end == end
    # Start should be 1 year before end
    expected_start = end.shift(years=-1)
    assert protocol.timeframe.start == expected_start


@pytest.mark.django_db
def test_create_condition_with_coding_basic() -> None:
    """Test creating a condition with coding from ValueSet."""
    patient: Patient = PatientFactory.create()

    condition = create_condition_with_coding(patient=patient, value_set_class=DiabetesValueSet)

    assert isinstance(condition, Condition)
    assert condition.patient == patient
    assert condition.codings.exists()

    # Should have at least one coding that matches the ValueSet
    coding = condition.codings.first()
    all_codes = DiabetesValueSet.get_codes()
    assert coding is not None
    assert coding.code in all_codes


@pytest.mark.django_db
def test_create_condition_with_coding_custom_onset_date() -> None:
    """Test creating a condition with custom onset date."""
    patient: Patient = PatientFactory.create()
    onset = arrow.get("2023-03-15").date()

    condition = create_condition_with_coding(
        patient=patient, value_set_class=DiabetesValueSet, onset_date=onset
    )

    assert condition.onset_date == onset


@pytest.mark.django_db
def test_create_condition_with_coding_arrow_onset_date() -> None:
    """Test creating a condition with arrow onset date."""
    patient: Patient = PatientFactory.create()
    onset_arrow = arrow.get("2023-03-15")

    condition = create_condition_with_coding(
        patient=patient, value_set_class=DiabetesValueSet, onset_date=onset_arrow
    )

    assert condition.onset_date == onset_arrow.date()


@pytest.mark.django_db
def test_create_condition_with_coding_non_surgical() -> None:
    """Test creating a non-surgical condition."""
    patient: Patient = PatientFactory.create()

    condition = create_condition_with_coding(
        patient=patient, value_set_class=DiabetesValueSet, surgical=False
    )

    assert condition.surgical is False


@pytest.mark.django_db
def test_create_condition_with_coding_custom_resolution() -> None:
    """Test creating a condition with custom resolution date."""
    patient: Patient = PatientFactory.create()
    resolution = arrow.get("2024-12-31").date()

    condition = create_condition_with_coding(
        patient=patient, value_set_class=DiabetesValueSet, resolution_date=resolution
    )

    assert condition.resolution_date == resolution


@pytest.mark.django_db
def test_create_condition_with_coding_finds_by_valueset() -> None:
    """Test that created condition can be found by ValueSet queries."""
    patient: Patient = PatientFactory.create()

    condition = create_condition_with_coding(patient=patient, value_set_class=DiabetesValueSet)

    # Should be found by .find() method
    from canvas_sdk.v1.data.condition import Condition

    found = Condition.objects.filter(patient=patient).find(DiabetesValueSet)

    assert condition in found


@pytest.mark.django_db
def test_create_encounter_with_billing_basic() -> None:
    """Test creating an encounter with billing from ValueSet."""
    patient: Patient = PatientFactory.create()
    encounter_date = arrow.get("2023-06-15")

    note, billing = create_encounter_with_billing(
        patient=patient, encounter_date=encounter_date, value_set_class=OfficeVisitValueSet
    )

    assert isinstance(note, Note)
    assert isinstance(billing, BillingLineItem)
    assert note.patient == patient
    assert billing.patient == patient
    assert billing.note == note

    # CPT code should be from the ValueSet
    all_codes = OfficeVisitValueSet.get_codes()
    assert billing.cpt in all_codes


@pytest.mark.django_db
def test_create_encounter_with_billing_explicit_cpt() -> None:
    """Test creating an encounter with explicit CPT code."""
    patient: Patient = PatientFactory.create()
    encounter_date = arrow.now()

    note, billing = create_encounter_with_billing(
        patient=patient, encounter_date=encounter_date, cpt_code="99214"
    )

    assert billing.cpt == "99214"


@pytest.mark.django_db
def test_create_encounter_with_billing_default_cpt() -> None:
    """Test creating an encounter with default CPT (no ValueSet or code)."""
    patient: Patient = PatientFactory.create()
    encounter_date = arrow.now()

    note, billing = create_encounter_with_billing(patient=patient, encounter_date=encounter_date)

    assert billing.cpt == "99213"  # Default office visit code


@pytest.mark.django_db
def test_create_encounter_with_billing_date_object() -> None:
    """Test creating an encounter with date object instead of arrow."""
    patient: Patient = PatientFactory.create()
    encounter_date = arrow.get("2023-06-15").date()

    note, billing = create_encounter_with_billing(
        patient=patient, encounter_date=encounter_date, cpt_code="99213"
    )

    assert note.datetime_of_service is not None
    assert billing.note == note


@pytest.mark.django_db
def test_create_encounter_with_billing_prefers_hcpcs() -> None:
    """Test that HCPCS codes are preferred over CPT when both exist."""
    patient: Patient = PatientFactory.create()
    encounter_date = arrow.now()

    note, billing = create_encounter_with_billing(
        patient=patient, encounter_date=encounter_date, value_set_class=OfficeVisitValueSet
    )

    # Should prefer HCPCS if available
    if "G0463" in OfficeVisitValueSet.values.get("HCPCS", []):
        assert billing.cpt == "G0463"


@pytest.mark.django_db
def test_create_encounter_with_billing_note_date_matches() -> None:
    """Test that note's datetime_of_service matches the encounter date."""
    patient: Patient = PatientFactory.create()
    encounter_date = arrow.get("2023-07-20")

    note, billing = create_encounter_with_billing(
        patient=patient, encounter_date=encounter_date, cpt_code="99213"
    )

    # Note's datetime should match encounter date
    assert note.datetime_of_service.date() == encounter_date.date()


@pytest.mark.django_db
def test_create_imaging_report_with_coding_basic() -> None:
    """Test creating an imaging report with coding from ValueSet."""
    patient: Patient = PatientFactory.create()

    report = create_imaging_report_with_coding(patient=patient, value_set_class=MammographyValueSet)

    assert isinstance(report, ImagingReport)
    assert report.patient == patient
    assert report.codings.exists()

    # Should have at least one coding that matches the ValueSet
    coding = report.codings.first()
    all_codes = MammographyValueSet.get_codes()
    assert coding is not None
    assert coding.code in all_codes


@pytest.mark.django_db
def test_create_imaging_report_with_coding_custom_dates() -> None:
    """Test creating an imaging report with custom dates."""
    patient: Patient = PatientFactory.create()
    original = arrow.get("2023-03-15").date()
    result = arrow.get("2023-03-20").date()

    report = create_imaging_report_with_coding(
        patient=patient,
        value_set_class=MammographyValueSet,
        original_date=original,
        result_date=result,
    )

    assert report.original_date == original
    assert report.result_date == result


@pytest.mark.django_db
def test_create_imaging_report_with_coding_arrow_dates() -> None:
    """Test creating an imaging report with arrow date objects."""
    patient: Patient = PatientFactory.create()
    original_arrow = arrow.get("2023-03-15")

    report = create_imaging_report_with_coding(
        patient=patient, value_set_class=MammographyValueSet, original_date=original_arrow
    )

    assert report.original_date == original_arrow.date()
    # result_date should default to original_date
    assert report.result_date == original_arrow.date()


@pytest.mark.django_db
def test_create_imaging_report_with_coding_finds_by_valueset() -> None:
    """Test that created imaging report can be found by ValueSet queries."""
    patient: Patient = PatientFactory.create()

    report = create_imaging_report_with_coding(patient=patient, value_set_class=MammographyValueSet)

    # Should be found by .find() method
    found = ImagingReport.objects.filter(patient=patient).find(MammographyValueSet)

    assert report in found


@pytest.mark.django_db
def test_create_imaging_report_with_coding_not_found_by_other_valueset() -> None:
    """Test that imaging report is not found by different ValueSet."""
    patient: Patient = PatientFactory.create()

    report = create_imaging_report_with_coding(patient=patient, value_set_class=MammographyValueSet)

    # Should NOT be found by DiabetesValueSet (different codes)
    found = ImagingReport.objects.filter(patient=patient).find(DiabetesValueSet)

    assert report not in found


@pytest.mark.django_db
def test_create_imaging_report_with_additional_kwargs() -> None:
    """Test creating imaging report with additional factory kwargs."""
    patient: Patient = PatientFactory.create()

    report = create_imaging_report_with_coding(
        patient=patient,
        value_set_class=MammographyValueSet,
        junked=True,
        requires_signature=True,
    )

    assert report.junked is True
    assert report.requires_signature is True
