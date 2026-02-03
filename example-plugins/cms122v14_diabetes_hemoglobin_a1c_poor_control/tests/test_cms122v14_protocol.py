"""Tests for CMS122v14 Diabetes Glycemic Status Protocol."""

from unittest.mock import Mock

import arrow
import pytest
from cms122v14_diabetes_hemoglobin_a1c_poor_control.protocols.cms122v14_protocol import (
    CMS122v14DiabetesGlycemicStatusPoorControl,
)

from canvas_sdk.effects.protocol_card.protocol_card import ProtocolCard
from canvas_sdk.test_utils.factories import (
    ClaimFactory,
    EncounterFactory,
    NoteFactory,
    PatientFactory,
)
from canvas_sdk.test_utils.helpers import (
    SNOMED_CT_SYSTEM,
    create_condition_with_coding,
    create_medication_with_coding,
    create_note_type,
    create_observation_with_value_coding,
    create_protocol_instance,
    extract_card,
    get_value_set_code,
    set_protocol_patient_context,
)
from canvas_sdk.v1.data import Device
from canvas_sdk.v1.data.claim_line_item import ClaimLineItem, ClaimLineItemStatus
from canvas_sdk.v1.data.condition import Condition
from canvas_sdk.v1.data.note import Note, PracticeLocationPOS
from canvas_sdk.v1.data.patient import Patient
from canvas_sdk.value_set.v2026.condition import (
    AdvancedIllness,
    Diabetes,
    FrailtyDiagnosis,
    HospiceDiagnosis,
)
from canvas_sdk.value_set.v2026.device import FrailtyDevice
from canvas_sdk.value_set.v2026.encounter import (
    EncounterInpatient,
    NursingFacilityVisit,
    OfficeVisit,
)
from canvas_sdk.value_set.v2026.medication import DementiaMedications


@pytest.fixture
def now() -> arrow.Arrow:
    """Fixed timestamp for consistent test dates."""
    return arrow.get("2026-12-31T12:00:00Z")


@pytest.fixture
def protocol_instance(now: arrow.Arrow) -> CMS122v14DiabetesGlycemicStatusPoorControl:
    """Create a protocol instance for testing."""
    timeframe_start = arrow.get("2026-01-01T00:00:00Z")
    timeframe_end = now
    return create_protocol_instance(
        CMS122v14DiabetesGlycemicStatusPoorControl,
        timeframe_start=timeframe_start,
        timeframe_end=timeframe_end,
    )


@pytest.fixture
def patient_age_50(now: arrow.Arrow) -> Patient:
    """Patient aged 50 (within 18-75 range)."""
    return PatientFactory.create(birth_date=now.shift(years=-50).date())


@pytest.fixture
def patient_age_70(now: arrow.Arrow) -> Patient:
    """Patient aged 70 (for age 66+ exclusion tests)."""
    return PatientFactory.create(birth_date=now.shift(years=-70).date())


@pytest.fixture
def diabetes_condition_age_50(patient_age_50: Patient, now: arrow.Arrow) -> Condition:
    """Create a diabetes condition for patient_age_50."""
    return create_condition_with_coding(
        patient=patient_age_50,
        value_set=Diabetes,
        onset_date=now.shift(months=-12).date(),
        display="Diabetes condition",
    )


@pytest.fixture
def diabetes_condition_age_70(patient_age_70: Patient, now: arrow.Arrow) -> Condition:
    """Create a diabetes condition for patient_age_70."""
    return create_condition_with_coding(
        patient=patient_age_70,
        value_set=Diabetes,
        onset_date=now.shift(months=-12).date(),
        display="Diabetes condition",
    )


@pytest.fixture
def eligible_note(patient_age_50: Patient, now: arrow.Arrow) -> Note:
    """Create an eligible encounter note for patient_age_50."""
    note = NoteFactory.create(
        patient=patient_age_50, datetime_of_service=now.shift(months=-6).datetime
    )
    office_visit_codes = list(getattr(OfficeVisit, "SNOMEDCT", []) or [])
    if not office_visit_codes:
        office_visit_codes = list(getattr(OfficeVisit, "CPT", []) or [])
    if office_visit_codes:
        note_type = create_note_type(
            now, office_visit_codes[0], "Office Visit", PracticeLocationPOS.OFFICE
        )
        note.note_type_version = note_type
        note.save()
    return note


@pytest.fixture
def eligible_note_age_70(patient_age_70: Patient, now: arrow.Arrow) -> Note:
    """Create an eligible encounter note for patient_age_70."""
    note = NoteFactory.create(
        patient=patient_age_70, datetime_of_service=now.shift(months=-6).datetime
    )
    office_visit_codes = list(getattr(OfficeVisit, "SNOMEDCT", []) or [])
    if not office_visit_codes:
        office_visit_codes = list(getattr(OfficeVisit, "CPT", []) or [])
    if office_visit_codes:
        note_type = create_note_type(
            now, office_visit_codes[0], "Office Visit", PracticeLocationPOS.OFFICE
        )
        note.note_type_version = note_type
        note.save()
    return note


def test_get_value_set_codes_extracts_from_multiple_attributes(
    protocol_instance: CMS122v14DiabetesGlycemicStatusPoorControl,
) -> None:
    """Test that codes are combined from multiple value set attributes."""

    class MockValueSet:
        SNOMEDCT = {"123456", "789012"}
        CPT = {"99213", "99214"}

    codes = protocol_instance._get_value_set_codes(MockValueSet, "SNOMEDCT", "CPT")
    assert codes == {"123456", "789012", "99213", "99214"}


def test_get_value_set_codes_handles_missing_attributes(
    protocol_instance: CMS122v14DiabetesGlycemicStatusPoorControl,
) -> None:
    """Test graceful handling when requested attribute doesn't exist."""

    class MockValueSet:
        SNOMEDCT = {"123456"}

    codes = protocol_instance._get_value_set_codes(MockValueSet, "SNOMEDCT", "ICD10CM")
    assert codes == {"123456"}


def test_get_value_set_codes_returns_empty_for_missing_attributes(
    protocol_instance: CMS122v14DiabetesGlycemicStatusPoorControl,
) -> None:
    """Test returns empty set when no requested attributes exist."""

    class MockValueSet:
        pass

    codes = protocol_instance._get_value_set_codes(MockValueSet, "SNOMEDCT", "CPT")
    assert codes == set()


@pytest.mark.parametrize("age", [0, 10, 17])
def test_age_below_18_not_in_population(
    protocol_instance: CMS122v14DiabetesGlycemicStatusPoorControl, age: int
) -> None:
    """Test patients below age 18 are excluded."""
    patient = Mock()
    assert protocol_instance._in_initial_population(patient, age) is False


@pytest.mark.parametrize("age", [76, 80, 100])
def test_age_above_75_not_in_population(
    protocol_instance: CMS122v14DiabetesGlycemicStatusPoorControl, age: int
) -> None:
    """Test patients above age 75 are excluded."""
    patient = Mock()
    assert protocol_instance._in_initial_population(patient, age) is False


def test_get_test_type_returns_hba1c_for_non_gmi_code(
    protocol_instance: CMS122v14DiabetesGlycemicStatusPoorControl,
) -> None:
    """Test HbA1c is returned when coding doesn't match GMI."""
    mock_lab_report = Mock()
    mock_lab_value = Mock()
    mock_coding = Mock()
    mock_coding.code = "4548-4"
    mock_lab_value.codings.all.return_value = [mock_coding]
    mock_lab_report.values.first.return_value = mock_lab_value

    assert protocol_instance._get_test_type(mock_lab_report) == "HbA1c"


def test_get_test_type_returns_gmi_for_gmi_code(
    protocol_instance: CMS122v14DiabetesGlycemicStatusPoorControl,
) -> None:
    """Test GMI is returned when coding matches GMI LOINC code."""
    mock_lab_report = Mock()
    mock_lab_value = Mock()
    mock_coding = Mock()
    mock_coding.code = "97506-0"
    mock_lab_value.codings.all.return_value = [mock_coding]
    mock_lab_report.values.first.return_value = mock_lab_value

    assert protocol_instance._get_test_type(mock_lab_report) == "GMI"


def test_get_test_type_returns_hba1c_when_no_lab_value(
    protocol_instance: CMS122v14DiabetesGlycemicStatusPoorControl,
) -> None:
    """Test defaults to HbA1c when no lab value exists."""
    mock_lab_report = Mock()
    mock_lab_report.values.first.return_value = None

    assert protocol_instance._get_test_type(mock_lab_report) == "HbA1c"


def test_get_glycemic_value_extracts_numeric_value(
    protocol_instance: CMS122v14DiabetesGlycemicStatusPoorControl,
) -> None:
    """Test extraction of numeric glycemic value."""
    mock_lab_report = Mock()
    mock_lab_value = Mock()
    mock_lab_value.value = 8.5
    mock_lab_report.values.first.return_value = mock_lab_value

    assert protocol_instance._get_glycemic_value(mock_lab_report) == 8.5


def test_get_glycemic_value_extracts_string_value(
    protocol_instance: CMS122v14DiabetesGlycemicStatusPoorControl,
) -> None:
    """Test extraction of string glycemic value."""
    mock_lab_report = Mock()
    mock_lab_value = Mock()
    mock_lab_value.value = "9.2"
    mock_lab_report.values.first.return_value = mock_lab_value

    assert protocol_instance._get_glycemic_value(mock_lab_report) == 9.2


def test_get_glycemic_value_returns_none_for_empty_string(
    protocol_instance: CMS122v14DiabetesGlycemicStatusPoorControl,
) -> None:
    """Test returns None when value is empty string."""
    mock_lab_report = Mock()
    mock_lab_value = Mock()
    mock_lab_value.value = ""
    mock_lab_report.values.first.return_value = mock_lab_value

    assert protocol_instance._get_glycemic_value(mock_lab_report) is None


def test_get_glycemic_value_returns_none_for_none_value(
    protocol_instance: CMS122v14DiabetesGlycemicStatusPoorControl,
) -> None:
    """Test returns None when value is None."""
    mock_lab_report = Mock()
    mock_lab_value = Mock()
    mock_lab_value.value = None
    mock_lab_report.values.first.return_value = mock_lab_value

    assert protocol_instance._get_glycemic_value(mock_lab_report) is None


def test_get_glycemic_value_returns_none_when_no_lab_value(
    protocol_instance: CMS122v14DiabetesGlycemicStatusPoorControl,
) -> None:
    """Test returns None when no lab value exists."""
    mock_lab_report = Mock()
    mock_lab_report.values.first.return_value = None

    assert protocol_instance._get_glycemic_value(mock_lab_report) is None


@pytest.mark.django_db
def test_inpatient_discharge_to_hospice_excludes(
    now: arrow.Arrow,
    protocol_instance: CMS122v14DiabetesGlycemicStatusPoorControl,
    patient_age_50: Patient,
    diabetes_condition_age_50: Condition,
    eligible_note: Note,
) -> None:
    """Test that inpatient encounter with discharge disposition to hospice excludes patient."""
    inpatient_codes = list(getattr(EncounterInpatient, "SNOMEDCT", []) or [])
    if not inpatient_codes:
        pytest.skip("EncounterInpatient codes missing")

    inpatient_note = NoteFactory.create(
        patient=patient_age_50,
        datetime_of_service=now.shift(months=-6).datetime,
    )
    note_type = create_note_type(
        now, inpatient_codes[0], "Inpatient Encounter", PracticeLocationPOS.INPATIENT_HOSPITAL
    )
    inpatient_note.note_type_version = note_type
    inpatient_note.save()

    EncounterFactory.create(
        note=inpatient_note,
        end_time=now.shift(months=-6).datetime,
    )

    create_observation_with_value_coding(
        patient=patient_age_50,
        note_id=inpatient_note.dbid,
        effective_datetime=now.shift(months=-6),
        code="428361000124107",
        system=SNOMED_CT_SYSTEM,
        display="Discharge to home for hospice care",
        name="Discharge disposition",
    )

    set_protocol_patient_context(protocol_instance, patient_age_50.id)
    card = extract_card(protocol_instance.compute())

    assert card["status"] == ProtocolCard.Status.NOT_APPLICABLE.value


@pytest.mark.django_db
def test_hospice_diagnosis_excludes(
    now: arrow.Arrow,
    protocol_instance: CMS122v14DiabetesGlycemicStatusPoorControl,
    patient_age_50: Patient,
    diabetes_condition_age_50: Condition,
    eligible_note: Note,
) -> None:
    """Test that hospice diagnosis excludes patient."""
    code_info = get_value_set_code(HospiceDiagnosis)
    if not code_info:
        pytest.skip("HospiceDiagnosis codes missing")

    create_condition_with_coding(
        patient=patient_age_50,
        value_set=HospiceDiagnosis,
        onset_date=now.shift(months=-6).date(),
        display="Hospice diagnosis",
    )

    set_protocol_patient_context(protocol_instance, patient_age_50.id)
    card = extract_card(protocol_instance.compute())

    assert card["status"] == ProtocolCard.Status.NOT_APPLICABLE.value


@pytest.mark.django_db
def test_frailty_device_order_during_period_detected(
    now: arrow.Arrow,
    protocol_instance: CMS122v14DiabetesGlycemicStatusPoorControl,
    patient_age_70: Patient,
    diabetes_condition_age_70: Condition,
) -> None:
    """Test that frailty device order during measurement period is detected."""
    frailty_device_hcpcs = list(getattr(FrailtyDevice, "HCPCSLEVELII", []) or [])
    if not frailty_device_hcpcs:
        pytest.skip("FrailtyDevice HCPCS codes missing")

    note = NoteFactory.create(
        patient=patient_age_70,
        datetime_of_service=now.shift(months=-6).datetime,
    )

    claim = ClaimFactory.create(note=note)
    ClaimLineItem.objects.create(
        claim=claim,
        status=ClaimLineItemStatus.ACTIVE,
        charge=100.00,
        from_date=now.shift(months=-6).date().isoformat(),
        thru_date=now.shift(months=-6).date().isoformat(),
        narrative="Frailty device",
        ndc_code="",
        ndc_dosage="",
        ndc_measure="",
        place_of_service=PracticeLocationPOS.OFFICE,
        proc_code=frailty_device_hcpcs[0],
        display="Frailty Device",
        remote_chg_id="test",
        units=1,
        epsdt="",
        family_planning="",
    )

    assert protocol_instance._has_frailty_device_orders(patient_age_70) is True


@pytest.mark.django_db
def test_frailty_device_order_before_period_not_detected(
    now: arrow.Arrow,
    protocol_instance: CMS122v14DiabetesGlycemicStatusPoorControl,
    patient_age_70: Patient,
    diabetes_condition_age_70: Condition,
) -> None:
    """Test that frailty device order before measurement period is NOT detected."""
    note = NoteFactory.create(
        patient=patient_age_70,
        datetime_of_service=now.shift(years=-2).datetime,
    )

    Device.objects.create(
        patient=patient_age_70,
        note_id=note.dbid,
        status="ordered",
        labeled_contains_NRL=False,
        assigning_authority="test",
        scoping_entity="test",
        udi="test",
        di="test",
        issuing_agency="test",
        lot_number="test",
        brand_name="test",
        mri_safety_status="test",
        version_model_number="test",
        company_name="test",
        gmdnPTName="test",
        expiration_date=now.shift(years=1).date(),
        expiration_date_original="test",
        serial_number="test",
        manufacturing_date_original="test",
        manufacturing_date=now.shift(years=-1).date(),
        manufacturer="test",
        procedure_id=0,
    )

    assert protocol_instance._has_frailty_device_orders(patient_age_70) is False


@pytest.mark.django_db
def test_nursing_home_encounter_before_period_excludes(
    now: arrow.Arrow,
    protocol_instance: CMS122v14DiabetesGlycemicStatusPoorControl,
    patient_age_70: Patient,
    diabetes_condition_age_70: Condition,
    eligible_note_age_70: Note,
) -> None:
    """Test that nursing home encounter before measurement period (but on or before end) excludes patient."""
    nursing_codes = list(getattr(NursingFacilityVisit, "SNOMEDCT", []) or [])
    if not nursing_codes:
        pytest.skip("NursingFacilityVisit codes missing")

    note = NoteFactory.create(
        patient=patient_age_70,
        datetime_of_service=now.shift(years=-2).datetime,
    )
    note_type = create_note_type(
        now, nursing_codes[0], "Nursing Facility Visit", PracticeLocationPOS.NURSING
    )
    note.note_type_version = note_type
    note.save()

    EncounterFactory.create(
        note=note,
        start_time=now.shift(years=-2).datetime,
    )

    set_protocol_patient_context(protocol_instance, patient_age_70.id)
    card = extract_card(protocol_instance.compute())

    assert card["status"] == ProtocolCard.Status.NOT_APPLICABLE.value


@pytest.mark.django_db
def test_nursing_home_claim_before_period_excludes(
    now: arrow.Arrow,
    protocol_instance: CMS122v14DiabetesGlycemicStatusPoorControl,
    patient_age_70: Patient,
    diabetes_condition_age_70: Condition,
    eligible_note_age_70: Note,
) -> None:
    """Test that nursing home claim before measurement period (but on or before end) excludes patient."""
    nursing_cpt_codes = list(getattr(NursingFacilityVisit, "CPT", []) or [])
    if not nursing_cpt_codes:
        pytest.skip("NursingFacilityVisit CPT codes missing")

    note = NoteFactory.create(
        patient=patient_age_70,
        datetime_of_service=now.shift(years=-2).datetime,
    )

    claim = ClaimFactory.create(note=note)
    ClaimLineItem.objects.create(
        claim=claim,
        status=ClaimLineItemStatus.ACTIVE,
        charge=100.00,
        from_date=now.shift(years=-2).date().isoformat(),
        thru_date=now.shift(years=-2).date().isoformat(),
        narrative="Nursing facility visit",
        ndc_code="",
        ndc_dosage="",
        ndc_measure="",
        place_of_service=PracticeLocationPOS.NURSING,
        proc_code=nursing_cpt_codes[0],
        display="Nursing Facility Visit",
        remote_chg_id="test",
        units=1,
        epsdt="",
        family_planning="",
    )

    set_protocol_patient_context(protocol_instance, patient_age_70.id)
    card = extract_card(protocol_instance.compute())

    assert card["status"] == ProtocolCard.Status.NOT_APPLICABLE.value


@pytest.mark.django_db
def test_advanced_illness_in_prior_year_excludes(
    now: arrow.Arrow,
    protocol_instance: CMS122v14DiabetesGlycemicStatusPoorControl,
    patient_age_70: Patient,
    diabetes_condition_age_70: Condition,
    eligible_note_age_70: Note,
) -> None:
    """Test that advanced illness diagnosis in year before measurement period excludes patient."""
    advanced_illness_code_info = get_value_set_code(AdvancedIllness)
    if not advanced_illness_code_info:
        pytest.skip("AdvancedIllness codes missing")

    frailty_code_info = get_value_set_code(FrailtyDiagnosis)
    if not frailty_code_info:
        pytest.skip("FrailtyDiagnosis codes missing")

    create_condition_with_coding(
        patient=patient_age_70,
        value_set=FrailtyDiagnosis,
        onset_date=now.shift(months=-6).date(),
        display="Frailty diagnosis",
    )

    create_condition_with_coding(
        patient=patient_age_70,
        value_set=AdvancedIllness,
        onset_date=now.shift(years=-1, months=-6).date(),
        display="Advanced illness",
    )

    set_protocol_patient_context(protocol_instance, patient_age_70.id)
    card = extract_card(protocol_instance.compute())

    assert card["status"] == ProtocolCard.Status.NOT_APPLICABLE.value


@pytest.mark.django_db
def test_dementia_meds_in_prior_year_excludes(
    now: arrow.Arrow,
    protocol_instance: CMS122v14DiabetesGlycemicStatusPoorControl,
    patient_age_70: Patient,
    diabetes_condition_age_70: Condition,
    eligible_note_age_70: Note,
) -> None:
    """Test that dementia medications in year before measurement period excludes patient."""
    frailty_code_info = get_value_set_code(FrailtyDiagnosis)
    if not frailty_code_info:
        pytest.skip("FrailtyDiagnosis codes missing")

    dementia_med_codes = list(getattr(DementiaMedications, "RXNORM", []) or [])
    if not dementia_med_codes:
        pytest.skip("DementiaMedications codes missing")

    create_condition_with_coding(
        patient=patient_age_70,
        value_set=FrailtyDiagnosis,
        onset_date=now.shift(months=-6).date(),
        display="Frailty diagnosis",
    )

    create_medication_with_coding(
        patient=patient_age_70,
        value_set=DementiaMedications,
        start_date=now.shift(years=-1, months=-6),
        display="Dementia Medication",
    )

    set_protocol_patient_context(protocol_instance, patient_age_70.id)
    card = extract_card(protocol_instance.compute())

    assert card["status"] == ProtocolCard.Status.NOT_APPLICABLE.value
