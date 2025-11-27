"""Tests for CMS130v14 Colorectal Cancer Screening protocol."""

import json
import uuid
from typing import Iterable, Tuple

import arrow
import pytest

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.protocol_card.protocol_card import ProtocolCard
from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.test_utils.factories import CanvasUserFactory, NoteFactory, PatientFactory
from canvas_sdk.v1.data import (
    Condition,
    ConditionCoding,
    ImagingReport,
    ImagingReportCoding,
    LabReport,
    LabValue,
    LabValueCoding,
    Medication,
    MedicationCoding,
    NoteType,
    Observation,
    ObservationCoding,
    ObservationValueCoding,
    ReferralReport,
    ReferralReportCoding,
)
from canvas_sdk.v1.data.note import NoteTypeCategories, PracticeLocationPOS
from canvas_sdk.value_set.v2026.condition import (
    AdvancedIllness,
    FrailtyDiagnosis,
    HospiceDiagnosis,
    MalignantNeoplasmOfColon,
    PalliativeCareDiagnosis,
)
from canvas_sdk.value_set.v2026.diagnostic_study import CtColonography
from canvas_sdk.value_set.v2026.laboratory_test import FecalOccultBloodTestFobt, SdnaFitTest
from canvas_sdk.value_set.v2026.medication import DementiaMedications
from canvas_sdk.value_set.v2026.procedure import (
    Colonoscopy,
    FlexibleSigmoidoscopy,
    TotalColectomy,
)
from cms130v14_colorectal_cancer_screening.cms130v14_colorectal_cancer_screening.protocols.cms130v14_protocol import (
    CMS130v14ColorectalCancerScreening,
)


# ---------- Helpers ----------

def first_or_skip(codes: Iterable[str], reason: str) -> str:
    """Return first code or skip when value set is empty (env-dependent)."""
    codes = list(codes or [])
    if not codes:
        pytest.skip(reason)
    return codes[0]


def extract_card(effects) -> dict:
    """Return protocol card 'data' from a single effect."""
    assert len(effects) == 1, f"Expected 1 effect, got {len(effects)}"
    eff = effects[0]
    assert eff.type == EffectType.ADD_OR_UPDATE_PROTOCOL_CARD
    return json.loads(eff.payload)["data"]


def set_patient_context(protocol: CMS130v14ColorectalCancerScreening, patient_id):
    """Set patient context in protocol event."""
    protocol.event.context = {"patient": {"id": str(patient_id)}}


def create_patient_at_age(now, years: int):
    """Create a patient at the specified age."""
    return PatientFactory.create(birth_date=now.shift(years=-years).date())


def create_lab_report_with_loinc(patient, when_dt, code: str, name: str = "") -> Tuple[LabReport, LabValue]:
    """Create a lab report with LOINC coding."""
    report = LabReport.objects.create(
        patient=patient,
        original_date=when_dt,
        assigned_date=when_dt,
        date_performed=when_dt,
        junked=False,
        requires_signature=False,
        for_test_only=False,
        version=1,
    )
    value = LabValue.objects.create(
        report=report,
        value="Negative",
        units="",
        abnormal_flag="",
        reference_range="",
        low_threshold="",
        high_threshold="",
        comment="",
        observation_status="final",
    )
    LabValueCoding.objects.create(value=value, code=code, system="http://loinc.org", name=name or code)
    return report, value


def create_imaging_report_with_cpt(patient, when_date, when_assigned_dt, code: str, display: str, junked=False):
    """Create an imaging report with CPT coding."""
    report = ImagingReport.objects.create(
        patient=patient,
        original_date=when_date,
        result_date=when_date,
        assigned_date=when_assigned_dt,
        junked=junked,
        requires_signature=False,
        name=display,
    )
    ImagingReportCoding.objects.create(report=report, code=code, system="http://www.ama-assn.org/go/cpt",
                                       display=display)
    return report


def create_imaging_report_with_loinc(patient, when_date, when_assigned_dt, code: str, display: str, junked=False):
    """Create an imaging report with LOINC coding (for CT Colonography)."""
    report = ImagingReport.objects.create(
        patient=patient,
        original_date=when_date,
        result_date=when_date,
        assigned_date=when_assigned_dt,
        junked=junked,
        requires_signature=False,
        name=display,
    )
    ImagingReportCoding.objects.create(report=report, code=code, system="http://loinc.org", display=display)
    return report


def create_referral_report_with_cpt(patient, when_date, code: str, display: str, specialty="Gastroenterology",
                                    junked=False):
    """Create a referral report with CPT coding."""
    report = ReferralReport.objects.create(
        patient=patient,
        original_date=when_date,
        junked=junked,
        requires_signature=False,
        specialty=specialty,
    )
    ReferralReportCoding.objects.create(report=report, code=code, system="http://www.ama-assn.org/go/cpt",
                                        display=display)
    return report


def create_referral_report_with_loinc(patient, when_date, code: str, display: str, specialty="Gastroenterology",
                                      junked=False):
    """Create a referral report with LOINC coding (for CT Colonography)."""
    report = ReferralReport.objects.create(
        patient=patient,
        original_date=when_date,
        junked=junked,
        requires_signature=False,
        specialty=specialty,
    )
    ReferralReportCoding.objects.create(report=report, code=code, system="http://loinc.org", display=display)
    return report


def create_condition_with_coding(patient, onset_date, code: str, system: str, display: str, clinical_status="active",
                                 resolution_date=None):
    """Create a condition with coding."""
    user = CanvasUserFactory()
    if resolution_date is None:
        resolution_date = arrow.utcnow().shift(years=100).date() if clinical_status == "active" else onset_date
    condition = Condition.objects.create(
        patient=patient,
        onset_date=onset_date,
        resolution_date=resolution_date,
        clinical_status=clinical_status,
        deleted=False,
        surgical=False,
        committer=user,
    )
    ConditionCoding.objects.create(condition=condition, code=code, system=system, display=display)
    return condition


def create_ct_colonography_report(patient, now, years_ago, report_type="imaging"):
    """
    Create CT Colonography report (handles both CPT and LOINC codes).

    Args:
        patient: Patient instance
        now: Arrow datetime for current time
        years_ago: Years ago for report date
        report_type: "imaging" or "referral"

    Returns:
        Created report instance
    """
    cpt_codes = list(getattr(CtColonography, "CPT", []) or [])
    loinc_codes = list(getattr(CtColonography, "LOINC", []) or [])

    when_date = now.shift(years=-years_ago).date()
    when_dt = now.shift(years=-years_ago).datetime

    if cpt_codes:
        code = cpt_codes[0]
        if report_type == "imaging":
            return create_imaging_report_with_cpt(patient, when_date, when_dt, code, "CT Colonography")
        else:
            return create_referral_report_with_cpt(patient, when_date, code, "CT Colonography")
    elif loinc_codes:
        code = loinc_codes[0]
        if report_type == "imaging":
            return create_imaging_report_with_loinc(patient, when_date, when_dt, code, "CT Colonography")
        else:
            return create_referral_report_with_loinc(patient, when_date, code, "CT Colonography")
    else:
        pytest.skip("CT Colonography codes missing")


def create_eligible_note_for_patient(patient, now, eligible_note_fixture):
    """Create an eligible note for a patient using the note type from the fixture."""
    note = NoteFactory.create(patient=patient, datetime_of_service=now.shift(months=-6).datetime)
    note.note_type_version = eligible_note_fixture.note_type_version
    note.save()
    return note


def create_medication_with_coding(patient, start_date, code: str, system: str, display: str, end_date=None):
    """Create a medication with coding."""
    user = CanvasUserFactory()
    # If end_date is None, set it to a far future date to satisfy NOT NULL constraint
    if end_date is None:
        end_date = arrow.utcnow().shift(years=100).date()
    medication = Medication.objects.create(
        patient=patient,
        start_date=start_date,
        end_date=end_date,
        deleted=False,
        committer=user,
        erx_quantity=0.0,  # Required field
    )
    MedicationCoding.objects.create(medication=medication, code=code, system=system, display=display)
    return medication


def create_observation_with_coding(patient, effective_datetime, codings_code: str, codings_system: str,
                                   value_codings_code: str = None, value_codings_system: str = None):
    """Create an observation with coding."""
    note = NoteFactory.create(patient=patient, datetime_of_service=effective_datetime)
    observation = Observation.objects.create(
        patient=patient,
        note_id=note.dbid,
        effective_datetime=effective_datetime,
        category="vital-signs",
        units="",
        value="",
        name="Test Observation",
    )
    # Add codings (e.g., LOINC code for the observation type)
    ObservationCoding.objects.create(
        observation=observation,
        code=codings_code,
        system=codings_system,
        display="Test Observation",
    )
    # Add value codings if provided (e.g., SNOMED result)
    if value_codings_code and value_codings_system:
        ObservationValueCoding.objects.create(
            observation=observation,
            code=value_codings_code,
            system=value_codings_system,
            display="Test Result",
        )
    return observation


# ---------- Fixtures ----------

@pytest.fixture
def now():
    """Fixed timestamp for consistent test dates."""
    return arrow.get("2025-01-15T12:00:00Z")


@pytest.fixture
def protocol_instance(now):
    """Create a protocol instance for testing."""
    event_request = EventRequest(type=EventType.CRON, context='{"patient": {"id": "test-patient-id"}}')
    event = Event(event_request=event_request)
    protocol = CMS130v14ColorectalCancerScreening(event=event, secrets={}, environment={})
    protocol.now = now
    return protocol


@pytest.fixture
def patient_age_62(now):
    """Patient aged 62 (within 46-75 range)."""
    return create_patient_at_age(now, 62)


@pytest.fixture
def patient_age_46(now):
    """Patient aged 46 (at lower boundary)."""
    return create_patient_at_age(now, 46)


@pytest.fixture
def patient_age_45(now):
    """Patient aged 45 (below 46, excluded)."""
    return create_patient_at_age(now, 45)


@pytest.fixture
def patient_age_75(now):
    """Patient aged 75 (at upper boundary)."""
    return create_patient_at_age(now, 75)


@pytest.fixture
def patient_age_80(now):
    """Patient aged 80 (above 75, excluded)."""
    return create_patient_at_age(now, 80)


@pytest.fixture
def patient_age_66(now):
    """Patient aged 66 (for age 66+ exclusion tests)."""
    return create_patient_at_age(now, 66)


@pytest.fixture
def patient_age_70(now):
    """Patient aged 70 (for age 66+ exclusion tests)."""
    return create_patient_at_age(now, 70)


@pytest.fixture
def eligible_note(now, patient_age_62):
    """Encounter within period with NoteType coded as Office Visit (SNOMED 308335008)."""
    note = NoteFactory.create(patient=patient_age_62, datetime_of_service=now.shift(months=-6).datetime)

    note_type = NoteType.objects.create(
        code="308335008",
        system="http://snomed.info/sct",
        display="Office Visit",
        name="Office Visit",
        icon="office",
        category=NoteTypeCategories.ENCOUNTER,
        rank=1,
        is_default_appointment_type=False,
        is_scheduleable=True,
        is_telehealth=False,
        is_billable=True,
        defer_place_of_service_to_practice_location=False,
        available_places_of_service=[],
        default_place_of_service=PracticeLocationPOS.OFFICE,
        is_system_managed=False,
        is_visible=True,
        is_active=True,
        unique_identifier=uuid.uuid4(),
        deprecated_at=now.shift(years=100).datetime,
        is_patient_required=False,
        allow_custom_title=False,
        is_scheduleable_via_patient_portal=False,
        online_duration=0,
    )
    note.note_type_version = note_type
    note.save()
    return note


# ---------- Tests ----------

@pytest.mark.django_db
class TestComputeGuards:
    """Test guard clauses in compute method."""

    def test_returns_empty_when_no_patient_in_context(self, protocol_instance):
        """Test that compute returns empty list when no patient in context."""
        protocol_instance.event.context = {}
        assert protocol_instance.compute() == []

    def test_returns_empty_when_patient_not_found(self, protocol_instance):
        """Test that compute returns empty list when patient doesn't exist."""
        protocol_instance.event.context = {"patient": {"id": "00000000-0000-0000-0000-000000000000"}}
        assert protocol_instance.compute() == []


@pytest.mark.django_db
class TestDueNoScreening:
    """Scenario 1: Patient DUE (No Screening)."""

    def test_due_when_in_population_and_no_prior_screening(self, protocol_instance, patient_age_62, eligible_note):
        """Test that patient without screening gets DUE card with recommendations."""
        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == ProtocolCard.Status.DUE.value
        assert "colorectal cancer screening" in card["narrative"].lower()
        recommendations = card.get("recommendations", [])
        assert len(recommendations) > 0, "DUE card should have recommendations"


@pytest.mark.django_db
class TestNumeratorByLabs:
    """Scenarios 2-3: Lab Reports (FOBT, FIT-DNA)."""

    @pytest.mark.parametrize(
        "test_type,months_ago,value_set_class,expected_keyword",
        [
            ("FOBT", 3, FecalOccultBloodTestFobt, "fobt"),
            ("FIT-DNA", 18, SdnaFitTest, "fit"),  # 18 months = 1.5 years, within 2-year window (v14)
        ],
        ids=["fobt_within_1_year", "fitdna_within_2_years"],
    )
    def test_lab_screening_within_window_satisfies(
            self, now, protocol_instance, patient_age_62, eligible_note, test_type, months_ago, value_set_class,
            expected_keyword
    ):
        """Test that lab screenings within their lookback windows satisfy the protocol."""
        code = first_or_skip(value_set_class.LOINC, f"{test_type} LOINC set is empty")
        create_lab_report_with_loinc(patient_age_62, now.shift(months=-months_ago).datetime, code, test_type)
        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == ProtocolCard.Status.SATISFIED.value
        assert expected_keyword in card["narrative"].lower() or "screening" in card["narrative"].lower()


@pytest.mark.django_db
class TestNumeratorByProcedures:
    """Scenarios 4-6: Procedures (Colonoscopy, Flexible Sigmoidoscopy, CT Colonography)."""

    @pytest.mark.parametrize(
        "procedure_type,years_ago,value_set_class,code_attr,expected_keyword,report_type",
        [
            ("Colonoscopy", 5, Colonoscopy, "CPT", "colonoscopy", "imaging"),
            ("Flexible Sigmoidoscopy", 2, FlexibleSigmoidoscopy, "CPT", "sigmoidoscopy", "referral"),
        ],
        ids=["colonoscopy_within_9_years", "flexible_sigmoidoscopy_within_4_years"],
    )
    def test_procedure_within_lookback_satisfies(
            self, now, protocol_instance, patient_age_62, eligible_note, procedure_type, years_ago, value_set_class,
            code_attr, expected_keyword, report_type
    ):
        """Test that procedures within their lookback windows satisfy the protocol."""
        codes = list(getattr(value_set_class, code_attr, []) or [])
        if not codes:
            pytest.skip(f"{procedure_type} {code_attr} codes missing")
        code = codes[0]

        if report_type == "imaging":
            create_imaging_report_with_cpt(
                patient_age_62, when_date=now.shift(years=-years_ago).date(),
                when_assigned_dt=now.shift(years=-years_ago).datetime, code=code, display=procedure_type
            )
        else:
            create_referral_report_with_cpt(patient_age_62, when_date=now.shift(years=-years_ago).date(), code=code,
                                            display=procedure_type)

        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == ProtocolCard.Status.SATISFIED.value
        assert expected_keyword in card["narrative"].lower()

    def test_ct_colonography_within_4_years_satisfies(self, now, protocol_instance, patient_age_62, eligible_note):
        """Scenario 6: CT Colonography (handles both CPT and LOINC codes) - v14: 4 years lookback."""
        create_ct_colonography_report(patient_age_62, now, years_ago=2, report_type="imaging")
        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == ProtocolCard.Status.SATISFIED.value
        assert "colonography" in card["narrative"].lower()


@pytest.mark.django_db
class TestExclusionsNotApplicable:
    """Scenarios 7-12: Exclusions (NOT_APPLICABLE)."""

    @pytest.mark.parametrize("age", [45, 80], ids=["too_young_45", "too_old_80"])
    def test_age_out_of_range_is_not_applicable(self, now, protocol_instance, eligible_note, age):
        """Scenarios 7-8: Age outside 46-75 range → NOT_APPLICABLE."""
        patient = create_patient_at_age(now, age)
        create_eligible_note_for_patient(patient, now, eligible_note)
        set_patient_context(protocol_instance, patient.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == ProtocolCard.Status.NOT_APPLICABLE.value

    def test_no_encounter_is_due(self, now, protocol_instance, patient_age_62):
        """Scenario 9: Patient without eligible encounter - protocol uses optimistic rule."""
        # Protocol has optimistic rule that allows processing even without eligible encounter
        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == ProtocolCard.Status.DUE.value

    def test_hospice_place_of_service_within_period_is_not_applicable(self, now, protocol_instance, patient_age_62,
                                                                      eligible_note):
        """Scenario 10: Hospice exclusion via discharge to hospice observation."""
        # Create a note first (required for observation)
        note = NoteFactory.create(
            patient=patient_age_62,
            datetime_of_service=now.shift(months=-6).datetime,
        )

        # Create observation with discharge to hospice SNOMED code (discharge disposition)
        observation = Observation.objects.create(
            patient=patient_age_62,
            note_id=note.dbid,
            effective_datetime=now.shift(months=-6).datetime,
            category="vital-signs",
            units="",
            value="",
            name="Discharge disposition",
        )
        ObservationValueCoding.objects.create(
            observation=observation,
            code="428361000124107",  # Discharge to home for Hospice
            system="http://snomed.info/sct",
            display="Discharge to home for Hospice",
        )

        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == ProtocolCard.Status.NOT_APPLICABLE.value

    @pytest.mark.parametrize(
        "condition_name,value_set_class,code_attr_options,display",
        [
            ("Total Colectomy", TotalColectomy, ["SNOMEDCT", "CPT"], "Total Colectomy"),
            ("Colon Cancer", MalignantNeoplasmOfColon, ["SNOMEDCT", "ICD10CM"], "Malignant Neoplasm of Colon"),
        ],
        ids=["total_colectomy", "colon_cancer"],
    )
    def test_condition_exclusions(self, now, protocol_instance, patient_age_62, eligible_note, condition_name,
                                  value_set_class, code_attr_options, display):
        """Scenarios 11-12: Condition exclusions (Total Colectomy, Colon Cancer) - v14: date constraints."""
        # Try each code attribute option until we find one with codes
        codes = None
        system = None
        for code_attr in code_attr_options:
            codes = list(getattr(value_set_class, code_attr, []) or [])
            if codes:
                if code_attr == "SNOMEDCT":
                    system = "http://snomed.info/sct"
                elif code_attr == "CPT":
                    system = "http://www.ama-assn.org/go/cpt"
                elif code_attr == "ICD10CM":
                    system = "http://hl7.org/fhir/sid/icd-10"
                break

        if not codes:
            pytest.skip(f"{condition_name} codes missing in this environment")

        # For colorectal cancer: onset_date <= end of measurement period
        # For total colectomy: resolution_date <= end of measurement period (or active with onset <= end)
        if condition_name == "Colon Cancer":
            create_condition_with_coding(
                patient_age_62,
                onset_date=now.shift(months=-6).date(),
                code=codes[0],
                system=system,
                display=display,
                clinical_status="active",
            )
        else:  # Total Colectomy
            create_condition_with_coding(
                patient_age_62,
                onset_date=now.shift(years=-2).date(),
                code=codes[0],
                system=system,
                display=display,
                clinical_status="resolved",
                resolution_date=now.shift(months=-6).date(),  # Resolved within measurement period
            )

        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == ProtocolCard.Status.NOT_APPLICABLE.value


@pytest.mark.django_db
class TestDueWhenScreeningsStale:
    """Scenarios 13-14: DUE (Screening Too Old)."""

    @pytest.mark.parametrize(
        "months_ago,value_set_class,test_name",
        [
            (24, FecalOccultBloodTestFobt, "FOBT"),
            (30, SdnaFitTest, "FIT-DNA"),  # v14: 2 years = 24 months, so 30 months is too old
        ],
        ids=["fobt_too_old", "fitdna_too_old"],
    )
    def test_lab_screenings_outside_window_yield_due(self, now, protocol_instance, patient_age_62, eligible_note,
                                                     months_ago, value_set_class, test_name):
        """Test that lab screenings outside their lookback windows yield DUE."""
        code = first_or_skip(value_set_class.LOINC, f"{test_name} LOINC empty")
        create_lab_report_with_loinc(patient_age_62, now.shift(months=-months_ago).datetime, code, test_name)
        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == ProtocolCard.Status.DUE.value

    @pytest.mark.parametrize(
        "years_ago,value_set_class,code_attr,display,report_type",
        [
            (10, Colonoscopy, "CPT", "Colonoscopy", "imaging"),  # v14: 9 years, so 10 is too old
            (5, FlexibleSigmoidoscopy, "CPT", "Flexible Sigmoidoscopy", "referral"),  # v14: 4 years, so 5 is too old
        ],
        ids=["colonoscopy_too_old", "flex_sig_too_old"],
    )
    def test_procedure_screenings_outside_window_yield_due(
            self, now, protocol_instance, patient_age_62, eligible_note, years_ago, value_set_class, code_attr, display,
            report_type
    ):
        """Test that procedure screenings outside their lookback windows yield DUE."""
        code = first_or_skip(getattr(value_set_class, code_attr, []), f"{display} {code_attr} empty")

        if report_type == "referral":
            create_referral_report_with_cpt(patient_age_62, now.shift(years=-years_ago).date(), code, display)
        else:
            create_imaging_report_with_cpt(
                patient_age_62,
                when_date=now.shift(years=-years_ago).date(),
                when_assigned_dt=now.shift(years=-years_ago).datetime,
                code=code,
                display=display,
            )

        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == ProtocolCard.Status.DUE.value

    def test_ct_colonography_too_old_yields_due(self, now, protocol_instance, patient_age_62, eligible_note):
        """Test that CT Colonography outside 4-year window (v14) yields DUE."""
        create_ct_colonography_report(patient_age_62, now, years_ago=5, report_type="imaging")
        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == ProtocolCard.Status.DUE.value


@pytest.mark.django_db
class TestImagingReports:
    """Scenarios 15-17: Imaging Reports."""

    @pytest.mark.parametrize(
        "procedure_type,years_ago,value_set_class,code_attr,expected_keyword",
        [
            ("Flexible Sigmoidoscopy", 2, FlexibleSigmoidoscopy, "CPT", "sigmoidoscopy"),
            ("Colonoscopy", 5, Colonoscopy, "CPT", "colonoscopy"),
        ],
        ids=["flexible_sigmoidoscopy", "colonoscopy"],
    )
    def test_imaging_report_satisfies(self, now, protocol_instance, patient_age_62, eligible_note, procedure_type,
                                      years_ago, value_set_class, code_attr, expected_keyword):
        """Scenarios 15, 17: Imaging Reports for procedures."""
        codes = list(getattr(value_set_class, code_attr, []) or [])
        if not codes:
            pytest.skip(f"{procedure_type} {code_attr} codes missing")
        code = codes[0]

        create_imaging_report_with_cpt(
            patient_age_62, when_date=now.shift(years=-years_ago).date(),
            when_assigned_dt=now.shift(years=-years_ago).datetime, code=code, display=procedure_type
        )
        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == ProtocolCard.Status.SATISFIED.value
        assert expected_keyword in card["narrative"].lower()

    def test_ct_colonography_imaging_report_satisfies(self, now, protocol_instance, patient_age_62, eligible_note):
        """Scenario 16: CT Colonography Imaging Report (handles both CPT and LOINC)."""
        create_ct_colonography_report(patient_age_62, now, years_ago=2, report_type="imaging")
        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == ProtocolCard.Status.SATISFIED.value
        assert "colonography" in card["narrative"].lower()


@pytest.mark.django_db
class TestReferralReports:
    """Scenarios 18-20: Referral Reports."""

    @pytest.mark.parametrize(
        "procedure_type,years_ago,value_set_class,code_attr,expected_keyword",
        [
            ("Flexible Sigmoidoscopy", 2, FlexibleSigmoidoscopy, "CPT", "sigmoidoscopy"),
            ("Colonoscopy", 5, Colonoscopy, "CPT", "colonoscopy"),
        ],
        ids=["flexible_sigmoidoscopy", "colonoscopy"],
    )
    def test_referral_report_satisfies(self, now, protocol_instance, patient_age_62, eligible_note, procedure_type,
                                       years_ago, value_set_class, code_attr, expected_keyword):
        """Scenarios 18, 20: Referral Reports for procedures."""
        codes = list(getattr(value_set_class, code_attr, []) or [])
        if not codes:
            pytest.skip(f"{procedure_type} {code_attr} codes missing")
        code = codes[0]

        create_referral_report_with_cpt(patient_age_62, when_date=now.shift(years=-years_ago).date(), code=code,
                                        display=procedure_type)
        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == ProtocolCard.Status.SATISFIED.value
        assert expected_keyword in card["narrative"].lower()

    def test_ct_colonography_referral_report_satisfies(self, now, protocol_instance, patient_age_62, eligible_note):
        """Scenario 19: CT Colonography Referral Report (handles both CPT and LOINC)."""
        create_ct_colonography_report(patient_age_62, now, years_ago=2, report_type="referral")
        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == ProtocolCard.Status.SATISFIED.value
        assert "colonography" in card["narrative"].lower()


@pytest.mark.django_db
class TestPriorityImagingBeforeReferral:
    """Scenarios 21-24: Priority Testing (Both Report Types)."""

    @pytest.mark.parametrize(
        "procedure_type,imaging_years_ago,referral_years_ago,value_set_class,code_attr,expected_keyword",
        [
            ("Flexible Sigmoidoscopy", 2, 1, FlexibleSigmoidoscopy, "CPT", "sigmoidoscopy"),
            ("Colonoscopy", 7, 6, Colonoscopy, "CPT", "colonoscopy"),
        ],
        ids=["flexible_sigmoidoscopy", "colonoscopy"],
    )
    def test_imaging_report_priority_over_referral(
            self, now, protocol_instance, patient_age_62, eligible_note, procedure_type, imaging_years_ago,
            referral_years_ago, value_set_class, code_attr, expected_keyword
    ):
        """Scenarios 21, 24: Imaging Report takes priority over Referral Report."""
        codes = list(getattr(value_set_class, code_attr, []) or [])
        if not codes:
            pytest.skip(f"{procedure_type} {code_attr} codes missing")
        code = codes[0]

        # Create Imaging Report (older date)
        imaging = create_imaging_report_with_cpt(
            patient_age_62,
            when_date=now.shift(years=-imaging_years_ago).date(),
            when_assigned_dt=now.shift(years=-imaging_years_ago).datetime,
            code=code,
            display=procedure_type,
        )
        # Create Referral Report (newer date)
        referral = create_referral_report_with_cpt(patient_age_62,
                                                   when_date=now.shift(years=-referral_years_ago).date(), code=code,
                                                   display=procedure_type)

        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == ProtocolCard.Status.SATISFIED.value
        # Should use Imaging Report (checked first), even though Referral is more recent
        # Verify the narrative contains the imaging report's date (2-digit year format) to confirm priority
        year_2digit = str(imaging.original_date.year)[-2:]
        assert year_2digit in card[
            "narrative"], f"Expected 2-digit year {year_2digit} in narrative: {card['narrative']}"
        assert expected_keyword in card["narrative"].lower()

    def test_referral_report_fallback_when_no_imaging_flexible_sigmoidoscopy(self, now, protocol_instance,
                                                                             patient_age_62, eligible_note):
        """Scenario 22: Referral Report used when Imaging Report doesn't exist."""
        cpt = first_or_skip(getattr(FlexibleSigmoidoscopy, "CPT", []), "Flexible Sigmoidoscopy CPT set is empty")
        create_referral_report_with_cpt(patient_age_62, when_date=now.shift(years=-2).date(), code=cpt,
                                        display="Flexible Sigmoidoscopy")
        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == ProtocolCard.Status.SATISFIED.value
        assert "sigmoidoscopy" in card["narrative"].lower()

    def test_imaging_report_priority_over_referral_ct_colonography(self, now, protocol_instance, patient_age_62,
                                                                   eligible_note):
        """Scenario 23: Imaging Report takes priority over Referral Report (CT Colonography)."""
        # Create imaging report (older)
        imaging = create_ct_colonography_report(patient_age_62, now, years_ago=3, report_type="imaging")
        # Create referral report (newer)
        referral = create_ct_colonography_report(patient_age_62, now, years_ago=2, report_type="referral")

        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == ProtocolCard.Status.SATISFIED.value
        # Should use Imaging Report (checked first) - verify by checking the date (2-digit year) in narrative
        year_2digit = str(imaging.original_date.year)[-2:]
        assert year_2digit in card[
            "narrative"], f"Expected 2-digit year {year_2digit} in narrative: {card['narrative']}"
        assert "colonography" in card["narrative"].lower()


@pytest.mark.django_db
class TestEdgeCases:
    """Scenarios 25-28: Edge Cases."""

    @pytest.mark.parametrize(
        "procedure_type,years_ago,value_set_class,code_attr,report_type",
        [
            ("Flexible Sigmoidoscopy", 5, FlexibleSigmoidoscopy, "CPT", "imaging"),  # v14: 4 years, so 5 is too old
            ("Colonoscopy", 10, Colonoscopy, "CPT", "referral"),  # v14: 9 years, so 10 is too old
        ],
        ids=["imaging_too_old_sigmoidoscopy", "referral_too_old_colonoscopy"],
    )
    def test_reports_too_old_yield_due(self, now, protocol_instance, patient_age_62, eligible_note, procedure_type,
                                       years_ago, value_set_class, code_attr, report_type):
        """Scenarios 25-26: Reports outside lookback period → DUE."""
        codes = list(getattr(value_set_class, code_attr, []) or [])
        if not codes:
            pytest.skip(f"{procedure_type} {code_attr} codes missing")
        code = codes[0]

        if report_type == "imaging":
            create_imaging_report_with_cpt(
                patient_age_62, when_date=now.shift(years=-years_ago).date(),
                when_assigned_dt=now.shift(years=-years_ago).datetime, code=code, display=procedure_type
            )
        else:
            create_referral_report_with_cpt(patient_age_62, when_date=now.shift(years=-years_ago).date(), code=code,
                                            display=procedure_type)

        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == ProtocolCard.Status.DUE.value

    @pytest.mark.parametrize(
        "procedure_type,value_set_class,code_attr,report_type",
        [
            ("Colonoscopy", Colonoscopy, "CPT", "imaging"),
            ("Flexible Sigmoidoscopy", FlexibleSigmoidoscopy, "CPT", "referral"),
        ],
        ids=["junked_imaging_colonoscopy", "junked_referral_sigmoidoscopy"],
    )
    def test_junked_reports_ignored(self, now, protocol_instance, patient_age_62, eligible_note, procedure_type,
                                    value_set_class, code_attr, report_type):
        """Scenario 27: Junked reports are ignored."""
        codes = list(getattr(value_set_class, code_attr, []) or [])
        if not codes:
            pytest.skip(f"{procedure_type} {code_attr} codes missing")
        code = codes[0]

        if report_type == "imaging":
            create_imaging_report_with_cpt(
                patient_age_62, when_date=now.shift(years=-5).date(), when_assigned_dt=now.shift(years=-5).datetime,
                code=code, display=procedure_type, junked=True
            )
        else:
            create_referral_report_with_cpt(patient_age_62, when_date=now.shift(years=-2).date(), code=code,
                                            display=procedure_type, junked=True)

        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == ProtocolCard.Status.DUE.value

    def test_ct_colonography_value_set_checked(self, now, protocol_instance, patient_age_62, eligible_note):
        """Scenario 28: CtColonography value set checked."""
        # Create report using one of the value sets (helper handles both CPT and LOINC)
        report = create_ct_colonography_report(patient_age_62, now, years_ago=2, report_type="imaging")
        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())

        # Verify the report is found and satisfies the protocol
        assert card["status"] == ProtocolCard.Status.SATISFIED.value
        assert "colonography" in card["narrative"].lower()
        # Verify the report's date (2-digit year format) appears in the narrative to confirm it was used
        year_2digit = str(report.original_date.year)[-2:]
        assert year_2digit in card[
            "narrative"], f"Expected 2-digit year {year_2digit} in narrative: {card['narrative']}"


@pytest.mark.django_db
class TestPriorityBasedScreening:
    """Priority-based screening selection (FOBT > FIT-DNA > etc.)."""

    def test_fobt_priority_over_fitdna(self, now, protocol_instance, patient_age_62, eligible_note):
        """Verify FOBT takes priority over FIT-DNA even if FIT-DNA is more recent."""
        fobt_code = first_or_skip(FecalOccultBloodTestFobt.LOINC, "FOBT LOINC empty")
        fitdna_code = first_or_skip(SdnaFitTest.LOINC, "FIT-DNA LOINC empty")

        # FOBT older (6 months ago)
        create_lab_report_with_loinc(patient_age_62, now.shift(months=-6).datetime, fobt_code, "FOBT")
        # FIT-DNA newer (2 months ago)
        create_lab_report_with_loinc(patient_age_62, now.shift(months=-2).datetime, fitdna_code, "FIT-DNA")

        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == ProtocolCard.Status.SATISFIED.value
        # Should show FOBT (priority 1) not FIT-DNA (priority 2)
        assert "fobt" in card["narrative"].lower()


@pytest.mark.django_db
class TestAgeBoundariesInPopulation:
    """Test age boundary conditions for initial population - v14: 46-75."""

    @pytest.mark.parametrize("age", [46, 75], ids=["exact_46", "exact_75"])
    def test_boundary_ages_in_population(self, now, protocol_instance, eligible_note, age):
        """Test that patients at exact boundary ages (46, 75) are in population."""
        patient = create_patient_at_age(now, age)
        create_eligible_note_for_patient(patient, now, eligible_note)
        set_patient_context(protocol_instance, patient.id)
        card = extract_card(protocol_instance.compute())

        # Verify patient is in population (not excluded)
        assert card["status"] != ProtocolCard.Status.NOT_APPLICABLE.value
        assert card["status"] in (ProtocolCard.Status.DUE.value, ProtocolCard.Status.SATISFIED.value)

    def test_45y_364d_is_in_population_with_floor_calc(self, now, protocol_instance, eligible_note):
        """Test that patient 45y 364d (one day before 46) is in population due to floor calculation."""
        patient = PatientFactory.create(birth_date=now.shift(years=-46, days=+1).date())
        create_eligible_note_for_patient(patient, now, eligible_note)
        set_patient_context(protocol_instance, patient.id)
        card = extract_card(protocol_instance.compute())

        # Verify patient is in population (not excluded due to age)
        assert card["status"] != ProtocolCard.Status.NOT_APPLICABLE.value
        assert card["status"] in (ProtocolCard.Status.DUE.value, ProtocolCard.Status.SATISFIED.value)

    def test_75y_plus_1d_is_in_population_with_floor_calc(self, now, protocol_instance, eligible_note):
        """Test that patient 75y + 1d (one day after 75) is in population due to floor calculation."""
        patient = PatientFactory.create(birth_date=now.shift(years=-75, days=-1).date())
        create_eligible_note_for_patient(patient, now, eligible_note)
        set_patient_context(protocol_instance, patient.id)
        card = extract_card(protocol_instance.compute())

        # Verify patient is in population (not excluded due to age)
        assert card["status"] != ProtocolCard.Status.NOT_APPLICABLE.value
        assert card["status"] in (ProtocolCard.Status.DUE.value, ProtocolCard.Status.SATISFIED.value)


@pytest.mark.django_db
class TestV14NewExclusions:
    """Tests for v14-specific denominator exclusions."""

    def test_age_66_plus_with_frailty_and_advanced_illness_excluded(
        self, now, protocol_instance, patient_age_70, eligible_note
    ):
        """Test that patient age 66+ with frailty and advanced illness is excluded."""
        # Create frailty diagnosis
        frailty_codes = list(getattr(FrailtyDiagnosis, "SNOMEDCT", []) or [])
        if not frailty_codes:
            pytest.skip("FrailtyDiagnosis codes missing")
        create_condition_with_coding(
            patient_age_70,
            onset_date=now.shift(months=-6).date(),
            code=frailty_codes[0],
            system="http://snomed.info/sct",
            display="Frailty",
            clinical_status="active",
        )

        # Create advanced illness diagnosis
        advanced_illness_codes = list(getattr(AdvancedIllness, "SNOMEDCT", []) or [])
        if not advanced_illness_codes:
            pytest.skip("AdvancedIllness codes missing")
        create_condition_with_coding(
            patient_age_70,
            onset_date=now.shift(months=-3).date(),
            code=advanced_illness_codes[0],
            system="http://snomed.info/sct",
            display="Advanced Illness",
            clinical_status="active",
        )

        create_eligible_note_for_patient(patient_age_70, now, eligible_note)
        set_patient_context(protocol_instance, patient_age_70.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == ProtocolCard.Status.NOT_APPLICABLE.value

    def test_age_66_plus_with_frailty_and_dementia_meds_excluded(
        self, now, protocol_instance, patient_age_70, eligible_note
    ):
        """Test that patient age 66+ with frailty and dementia medications is excluded."""
        # Create frailty diagnosis
        frailty_codes = list(getattr(FrailtyDiagnosis, "SNOMEDCT", []) or [])
        if not frailty_codes:
            pytest.skip("FrailtyDiagnosis codes missing")
        create_condition_with_coding(
            patient_age_70,
            onset_date=now.shift(months=-6).date(),
            code=frailty_codes[0],
            system="http://snomed.info/sct",
            display="Frailty",
            clinical_status="active",
        )

        # Create dementia medication
        dementia_med_codes = list(getattr(DementiaMedications, "RXNORM", []) or [])
        if not dementia_med_codes:
            pytest.skip("DementiaMedications codes missing")
        create_medication_with_coding(
            patient_age_70,
            start_date=now.shift(months=-3).date(),
            code=dementia_med_codes[0],
            system="http://www.nlm.nih.gov/research/umls/rxnorm",
            display="Dementia Medication",
        )

        create_eligible_note_for_patient(patient_age_70, now, eligible_note)
        set_patient_context(protocol_instance, patient_age_70.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == ProtocolCard.Status.NOT_APPLICABLE.value

    def test_age_66_plus_in_nursing_home_excluded(
        self, now, protocol_instance, patient_age_70, eligible_note
    ):
        """Test that patient age 66+ living in nursing home is excluded."""
        # Create housing status observation indicating nursing home
        # LOINC 71802-3 (Housing status) with value SNOMED 160734000 (Lives in nursing home)
        create_observation_with_coding(
            patient_age_70,
            effective_datetime=now.shift(months=-6).datetime,
            codings_code="71802-3",  # Housing status LOINC
            codings_system="http://loinc.org",
            value_codings_code="160734000",  # Lives in nursing home SNOMED
            value_codings_system="http://snomed.info/sct",
        )

        create_eligible_note_for_patient(patient_age_70, now, eligible_note)
        set_patient_context(protocol_instance, patient_age_70.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == ProtocolCard.Status.NOT_APPLICABLE.value

    def test_palliative_care_excluded(
        self, now, protocol_instance, patient_age_62, eligible_note
    ):
        """Test that patient receiving palliative care is excluded."""
        palliative_codes = list(getattr(PalliativeCareDiagnosis, "SNOMEDCT", []) or [])
        if not palliative_codes:
            pytest.skip("PalliativeCareDiagnosis codes missing")
        create_condition_with_coding(
            patient_age_62,
            onset_date=now.shift(months=-6).date(),
            code=palliative_codes[0],
            system="http://snomed.info/sct",
            display="Palliative Care",
            clinical_status="active",
        )

        create_eligible_note_for_patient(patient_age_62, now, eligible_note)
        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == ProtocolCard.Status.NOT_APPLICABLE.value

    def test_age_65_with_frailty_not_excluded(
        self, now, protocol_instance, eligible_note
    ):
        """Test that patient age 65 with frailty is NOT excluded (age must be 66+)."""
        patient = create_patient_at_age(now, 65)
        frailty_codes = list(getattr(FrailtyDiagnosis, "SNOMEDCT", []) or [])
        if not frailty_codes:
            pytest.skip("FrailtyDiagnosis codes missing")
        create_condition_with_coding(
            patient,
            onset_date=now.shift(months=-6).date(),
            code=frailty_codes[0],
            system="http://snomed.info/sct",
            display="Frailty",
            clinical_status="active",
        )

        create_eligible_note_for_patient(patient, now, eligible_note)
        set_patient_context(protocol_instance, patient.id)
        card = extract_card(protocol_instance.compute())

        # Should not be excluded (age < 66)
        assert card["status"] != ProtocolCard.Status.NOT_APPLICABLE.value
        assert card["status"] in (ProtocolCard.Status.DUE.value, ProtocolCard.Status.SATISFIED.value)

    def test_age_66_with_frailty_only_not_excluded(
        self, now, protocol_instance, patient_age_66, eligible_note
    ):
        """Test that patient age 66+ with frailty but NO advanced illness/dementia meds is NOT excluded."""
        frailty_codes = list(getattr(FrailtyDiagnosis, "SNOMEDCT", []) or [])
        if not frailty_codes:
            pytest.skip("FrailtyDiagnosis codes missing")
        create_condition_with_coding(
            patient_age_66,
            onset_date=now.shift(months=-6).date(),
            code=frailty_codes[0],
            system="http://snomed.info/sct",
            display="Frailty",
            clinical_status="active",
        )

        create_eligible_note_for_patient(patient_age_66, now, eligible_note)
        set_patient_context(protocol_instance, patient_age_66.id)
        card = extract_card(protocol_instance.compute())

        # Should not be excluded (frailty alone is not enough)
        assert card["status"] != ProtocolCard.Status.NOT_APPLICABLE.value
        assert card["status"] in (ProtocolCard.Status.DUE.value, ProtocolCard.Status.SATISFIED.value)


@pytest.mark.django_db
class TestV14NewEncounterTypes:
    """Tests for v14 new encounter types (Virtual Encounter, Telephone Visits)."""

    def test_virtual_encounter_qualifies(
        self, now, protocol_instance, patient_age_62
    ):
        """Test that Virtual Encounter qualifies for initial population."""
        # Create Virtual Encounter note type
        virtual_note_type = NoteType.objects.create(
            code="448337001",
            system="http://snomed.info/sct",
            display="Virtual Encounter",
            name="Virtual Encounter",
            icon="virtual",
            category=NoteTypeCategories.ENCOUNTER,
            rank=1,
            is_default_appointment_type=False,
            is_scheduleable=True,
            is_telehealth=True,
            is_billable=True,
            defer_place_of_service_to_practice_location=False,
            available_places_of_service=[],
            default_place_of_service=PracticeLocationPOS.OFFICE,
            is_system_managed=False,
            is_visible=True,
            is_active=True,
            unique_identifier=uuid.uuid4(),
            deprecated_at=now.shift(years=100).datetime,
            is_patient_required=False,
            allow_custom_title=False,
            is_scheduleable_via_patient_portal=False,
            online_duration=0,
        )

        note = NoteFactory.create(patient=patient_age_62, datetime_of_service=now.shift(months=-6).datetime)
        note.note_type_version = virtual_note_type
        note.save()

        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())

        # Should be in population (not excluded)
        assert card["status"] != ProtocolCard.Status.NOT_APPLICABLE.value
        assert card["status"] in (ProtocolCard.Status.DUE.value, ProtocolCard.Status.SATISFIED.value)

    def test_telephone_visit_qualifies(
        self, now, protocol_instance, patient_age_62
    ):
        """Test that Telephone Visit qualifies for initial population."""
        # Create Telephone Visit note type
        telephone_note_type = NoteType.objects.create(
            code="185349003",
            system="http://snomed.info/sct",
            display="Telephone Consultation",
            name="Telephone Consultation",
            icon="phone",
            category=NoteTypeCategories.ENCOUNTER,
            rank=1,
            is_default_appointment_type=False,
            is_scheduleable=True,
            is_telehealth=True,
            is_billable=True,
            defer_place_of_service_to_practice_location=False,
            available_places_of_service=[],
            default_place_of_service=PracticeLocationPOS.OFFICE,
            is_system_managed=False,
            is_visible=True,
            is_active=True,
            unique_identifier=uuid.uuid4(),
            deprecated_at=now.shift(years=100).datetime,
            is_patient_required=False,
            allow_custom_title=False,
            is_scheduleable_via_patient_portal=False,
            online_duration=0,
        )

        note = NoteFactory.create(patient=patient_age_62, datetime_of_service=now.shift(months=-6).datetime)
        note.note_type_version = telephone_note_type
        note.save()

        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())

        # Should be in population (not excluded)
        assert card["status"] != ProtocolCard.Status.NOT_APPLICABLE.value
        assert card["status"] in (ProtocolCard.Status.DUE.value, ProtocolCard.Status.SATISFIED.value)


@pytest.mark.django_db
class TestV14UpdatedLookbackPeriods:
    """Tests for v14 updated lookback periods."""

    @pytest.mark.parametrize(
        "months_ago,expected_status",
        [
            (18, ProtocolCard.Status.SATISFIED.value),  # Within 2-year window
            (30, ProtocolCard.Status.DUE.value),  # Outside 2-year window
        ],
        ids=["fit_dna_within_2_years", "fit_dna_outside_2_years"],
    )
    def test_fit_dna_lookback_period(self, now, protocol_instance, patient_age_62, eligible_note, months_ago, expected_status):
        """Test FIT-DNA lookback period (v14: 2 years)."""
        code = first_or_skip(SdnaFitTest.LOINC, "FIT-DNA LOINC empty")
        create_lab_report_with_loinc(patient_age_62, now.shift(months=-months_ago).datetime, code, "FIT-DNA")
        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == expected_status

    @pytest.mark.parametrize(
        "years_ago,expected_status",
        [
            (3, ProtocolCard.Status.SATISFIED.value),  # Within 4-year window
            (5, ProtocolCard.Status.DUE.value),  # Outside 4-year window
        ],
        ids=["flexible_sigmoidoscopy_within_4_years", "flexible_sigmoidoscopy_outside_4_years"],
    )
    def test_flexible_sigmoidoscopy_lookback_period(
        self, now, protocol_instance, patient_age_62, eligible_note, years_ago, expected_status
    ):
        """Test Flexible Sigmoidoscopy lookback period (v14: 4 years)."""
        codes = list(getattr(FlexibleSigmoidoscopy, "CPT", []) or [])
        if not codes:
            pytest.skip("FlexibleSigmoidoscopy CPT codes missing")
        create_referral_report_with_cpt(
            patient_age_62, when_date=now.shift(years=-years_ago).date(), code=codes[0], display="Flexible Sigmoidoscopy"
        )
        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == expected_status

    @pytest.mark.parametrize(
        "years_ago,expected_status",
        [
            (3, ProtocolCard.Status.SATISFIED.value),  # Within 4-year window
            (5, ProtocolCard.Status.DUE.value),  # Outside 4-year window
        ],
        ids=["ct_colonography_within_4_years", "ct_colonography_outside_4_years"],
    )
    def test_ct_colonography_lookback_period(
        self, now, protocol_instance, patient_age_62, eligible_note, years_ago, expected_status
    ):
        """Test CT Colonography lookback period (v14: 4 years)."""
        create_ct_colonography_report(patient_age_62, now, years_ago=years_ago, report_type="imaging")
        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == expected_status

    @pytest.mark.parametrize(
        "years_ago,expected_status",
        [
            (8, ProtocolCard.Status.SATISFIED.value),  # Within 9-year window
            (10, ProtocolCard.Status.DUE.value),  # Outside 9-year window
        ],
        ids=["colonoscopy_within_9_years", "colonoscopy_outside_9_years"],
    )
    def test_colonoscopy_lookback_period(
        self, now, protocol_instance, patient_age_62, eligible_note, years_ago, expected_status
    ):
        """Test Colonoscopy lookback period (v14: 9 years)."""
        codes = list(getattr(Colonoscopy, "CPT", []) or [])
        if not codes:
            pytest.skip("Colonoscopy CPT codes missing")
        create_imaging_report_with_cpt(
            patient_age_62,
            when_date=now.shift(years=-years_ago).date(),
            when_assigned_dt=now.shift(years=-years_ago).datetime,
            code=codes[0],
            display="Colonoscopy",
        )
        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == expected_status


@pytest.mark.django_db
class TestV14EdgeCases:
    """Additional edge case tests for v14."""

    def test_colon_cancer_onset_before_period_end_excluded(
        self, now, protocol_instance, patient_age_62, eligible_note
    ):
        """Test that colorectal cancer with onset on or before end of measurement period is excluded."""
        codes = list(getattr(MalignantNeoplasmOfColon, "SNOMEDCT", []) or list(getattr(MalignantNeoplasmOfColon, "ICD10CM", [])))
        if not codes:
            pytest.skip("MalignantNeoplasmOfColon codes missing")
        system = "http://snomed.info/sct" if getattr(MalignantNeoplasmOfColon, "SNOMEDCT", []) else "http://hl7.org/fhir/sid/icd-10"

        # Onset date before measurement period end
        create_condition_with_coding(
            patient_age_62,
            onset_date=now.shift(years=-2).date(),  # Before measurement period end
            code=codes[0],
            system=system,
            display="Malignant Neoplasm of Colon",
            clinical_status="active",
        )

        create_eligible_note_for_patient(patient_age_62, now, eligible_note)
        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == ProtocolCard.Status.NOT_APPLICABLE.value

    def test_total_colectomy_resolved_before_period_end_excluded(
        self, now, protocol_instance, patient_age_62, eligible_note
    ):
        """Test that total colectomy resolved on or before end of measurement period is excluded."""
        codes = list(getattr(TotalColectomy, "SNOMEDCT", []) or list(getattr(TotalColectomy, "CPT", [])))
        if not codes:
            pytest.skip("TotalColectomy codes missing")
        system = "http://snomed.info/sct" if getattr(TotalColectomy, "SNOMEDCT", []) else "http://www.ama-assn.org/go/cpt"

        # Resolved before measurement period end
        create_condition_with_coding(
            patient_age_62,
            onset_date=now.shift(years=-3).date(),
            code=codes[0],
            system=system,
            display="Total Colectomy",
            clinical_status="resolved",
            resolution_date=now.shift(months=-6).date(),  # Resolved within measurement period
        )

        create_eligible_note_for_patient(patient_age_62, now, eligible_note)
        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == ProtocolCard.Status.NOT_APPLICABLE.value