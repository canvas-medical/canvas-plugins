import uuid
from datetime import date, datetime
from unittest.mock import Mock

import arrow
import pytest
from cms122v14_diabetes_hemoglobin_a1c_poor_control.constants import (
    AGE_RANGE_END,
    AGE_RANGE_START,
    DISCHARGE_TO_FACILITY_HOSPICE_SNOMED,
    DISCHARGE_TO_HOME_HOSPICE_SNOMED,
    GLYCEMIC_THRESHOLD,
    GMI_LOINC_CODE,
    MNT_CPT_CODES,
    MNT_HCPCS_CODES,
    PROTOCOL_KEY,
    TEST_TYPE_GMI,
    TEST_TYPE_HBA1C,
)
from cms122v14_diabetes_hemoglobin_a1c_poor_control.protocols.cms122v14_protocol import (
    CMS122v14DiabetesGlycemicStatusPoorControl,
)

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.protocol_card.protocol_card import ProtocolCard
from canvas_sdk.events import EventType
from canvas_sdk.test_utils.factories import (
    ClaimFactory,
    EncounterFactory,
    NoteFactory,
    ObservationFactory,
    ObservationValueCodingFactory,
    PatientFactory,
)
from canvas_sdk.test_utils.helpers import (
    create_condition_with_coding,
    create_medication_with_coding,
    create_protocol_instance,
)
from canvas_sdk.v1.data import Device, NoteType
from canvas_sdk.v1.data.claim_line_item import ClaimLineItem, ClaimLineItemStatus
from canvas_sdk.v1.data.note import NoteTypeCategories, PracticeLocationPOS
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


class MockProtocol:
    """Mock protocol for testing helper methods without full initialization."""

    AGE_RANGE_START = AGE_RANGE_START
    AGE_RANGE_END = AGE_RANGE_END
    GLYCEMIC_THRESHOLD = GLYCEMIC_THRESHOLD
    GMI_LOINC_CODE = GMI_LOINC_CODE
    TEST_TYPE_GMI = TEST_TYPE_GMI
    TEST_TYPE_HBA1C = TEST_TYPE_HBA1C

    def __init__(self):
        self.event = Mock()
        self.event.type = EventType.PATIENT_UPDATED
        self.event.target = Mock()
        self.event.target.id = "test-patient-id"
        self.event.context = {"patient": {"id": "test-patient-id"}}

        # Mock timeframe
        self.timeframe = Mock()
        self.timeframe.start = Mock()
        self.timeframe.start.datetime = datetime(2026, 1, 1)
        self.timeframe.start.date.return_value = date(2026, 1, 1)
        self.timeframe.start.shift = Mock(
            return_value=Mock(
                datetime=datetime(2025, 1, 1), date=Mock(return_value=date(2025, 1, 1))
            )
        )
        self.timeframe.end = Mock()
        self.timeframe.end.datetime = datetime(2026, 12, 31)
        self.timeframe.end.date.return_value = date(2026, 12, 31)

        # Mock now
        self.now = Mock()
        self.now.shift = Mock(return_value=Mock(humanize=Mock(return_value="over 1 year ago")))

    # Copy methods from the real protocol for testing
    _get_value_set_codes = CMS122v14DiabetesGlycemicStatusPoorControl._get_value_set_codes
    _build_period_overlap_query = (
        CMS122v14DiabetesGlycemicStatusPoorControl._build_period_overlap_query
    )
    _in_initial_population = CMS122v14DiabetesGlycemicStatusPoorControl._in_initial_population
    _get_test_type = CMS122v14DiabetesGlycemicStatusPoorControl._get_test_type
    _get_glycemic_value = CMS122v14DiabetesGlycemicStatusPoorControl._get_glycemic_value
    relative_float = CMS122v14DiabetesGlycemicStatusPoorControl.relative_float


@pytest.fixture
def mock_protocol():
    """Create a mock protocol instance for testing."""
    return MockProtocol()


@pytest.fixture
def mock_lab_report():
    """Create a mock lab report for testing."""
    return Mock()


class TestEventConfiguration:
    """Test that protocol responds to correct event types."""

    @pytest.mark.parametrize(
        "event_type",
        [
            EventType.CONDITION_CREATED,
            EventType.CONDITION_UPDATED,
            EventType.CONDITION_RESOLVED,
        ],
    )
    def test_responds_to_condition_events(self, event_type):
        """Test that protocol responds to condition events."""
        assert EventType.Name(event_type) in CMS122v14DiabetesGlycemicStatusPoorControl.RESPONDS_TO

    @pytest.mark.parametrize(
        "event_type",
        [
            EventType.LAB_REPORT_CREATED,
            EventType.LAB_REPORT_UPDATED,
        ],
    )
    def test_responds_to_lab_report_events(self, event_type):
        """Test that protocol responds to lab report events."""
        assert EventType.Name(event_type) in CMS122v14DiabetesGlycemicStatusPoorControl.RESPONDS_TO

    @pytest.mark.parametrize(
        "event_type",
        [
            EventType.PATIENT_CREATED,
            EventType.PATIENT_UPDATED,
        ],
    )
    def test_responds_to_patient_events(self, event_type):
        """Test that protocol responds to patient events."""
        assert EventType.Name(event_type) in CMS122v14DiabetesGlycemicStatusPoorControl.RESPONDS_TO

    @pytest.mark.parametrize(
        "event_type",
        [
            EventType.ENCOUNTER_CREATED,
            EventType.ENCOUNTER_UPDATED,
        ],
    )
    def test_responds_to_encounter_events(self, event_type):
        """Test that protocol responds to encounter events (new in v14)."""
        assert EventType.Name(event_type) in CMS122v14DiabetesGlycemicStatusPoorControl.RESPONDS_TO

    @pytest.mark.parametrize(
        "event_type",
        [
            EventType.CLAIM_CREATED,
            EventType.CLAIM_UPDATED,
        ],
    )
    def test_responds_to_claim_events(self, event_type):
        """Test that protocol responds to claim events (new in v14)."""
        assert EventType.Name(event_type) in CMS122v14DiabetesGlycemicStatusPoorControl.RESPONDS_TO


class TestMetaConfiguration:
    """Test protocol metadata configuration."""

    def test_meta_title(self):
        """Test that meta title reflects v14 naming."""
        assert CMS122v14DiabetesGlycemicStatusPoorControl.Meta.title == (
            "Diabetes: Glycemic Status Assessment Greater Than 9%"
        )

    def test_meta_identifiers(self):
        """Test that CMS identifier is v14."""
        assert "CMS122v14" in CMS122v14DiabetesGlycemicStatusPoorControl.Meta.identifiers

    def test_meta_version(self):
        """Test that version indicates 2026 measurement period."""
        assert "2026" in CMS122v14DiabetesGlycemicStatusPoorControl.Meta.version


class TestProtocolConstants:
    """Test protocol constants match CMS122v14 specification."""

    def test_age_range_start(self):
        """Test minimum age is 18 years."""
        assert AGE_RANGE_START == 18

    def test_age_range_end(self):
        """Test maximum age is 75 years."""
        assert AGE_RANGE_END == 75

    def test_glycemic_threshold(self):
        """Test glycemic threshold is 9.0% per CMS122v14 spec."""
        assert GLYCEMIC_THRESHOLD == 9.0

    def test_gmi_loinc_code(self):
        """Test GMI LOINC code is 97506-0 (new in v14)."""
        assert GMI_LOINC_CODE == "97506-0"

    def test_protocol_key(self):
        """Test protocol key is CMS122v14."""
        assert PROTOCOL_KEY == "CMS122v14"

    def test_discharge_to_home_hospice_code(self):
        """Test discharge to home hospice SNOMED code."""
        assert DISCHARGE_TO_HOME_HOSPICE_SNOMED == "428361000124107"

    def test_discharge_to_facility_hospice_code(self):
        """Test discharge to facility hospice SNOMED code."""
        assert DISCHARGE_TO_FACILITY_HOSPICE_SNOMED == "428371000124100"

    @pytest.mark.parametrize("code", ["97802", "97803", "97804"])
    def test_mnt_cpt_codes(self, code):
        """Test Medical Nutrition Therapy CPT codes are defined."""
        assert code in MNT_CPT_CODES

    @pytest.mark.parametrize("code", ["G0270", "G0271"])
    def test_mnt_hcpcs_codes(self, code):
        """Test Medical Nutrition Therapy HCPCS codes are defined."""
        assert code in MNT_HCPCS_CODES


class TestGetValueSetCodes:
    """Test _get_value_set_codes helper method."""

    def test_extracts_codes_from_multiple_attributes(self, mock_protocol):
        """Test that codes are combined from multiple value set attributes."""

        class MockValueSet:
            SNOMEDCT = {"123456", "789012"}
            CPT = {"99213", "99214"}

        codes = mock_protocol._get_value_set_codes(MockValueSet, "SNOMEDCT", "CPT")
        assert codes == {"123456", "789012", "99213", "99214"}

    def test_handles_missing_attributes(self, mock_protocol):
        """Test graceful handling when requested attribute doesn't exist."""

        class MockValueSet:
            SNOMEDCT = {"123456"}

        codes = mock_protocol._get_value_set_codes(MockValueSet, "SNOMEDCT", "ICD10CM")
        assert codes == {"123456"}

    def test_returns_empty_set_for_all_missing_attributes(self, mock_protocol):
        """Test returns empty set when no requested attributes exist."""

        class MockValueSet:
            pass

        codes = mock_protocol._get_value_set_codes(MockValueSet, "SNOMEDCT", "CPT")
        assert codes == set()


class TestBuildPeriodOverlapQuery:
    """Test _build_period_overlap_query helper method."""

    def test_returns_q_object(self, mock_protocol):
        """Test that method returns a Django Q object."""
        query = mock_protocol._build_period_overlap_query(date(2026, 1, 1), date(2026, 12, 31))
        assert hasattr(query, "connector")

    def test_query_has_or_connector(self, mock_protocol):
        """Test that query uses OR logic for overlap conditions."""
        query = mock_protocol._build_period_overlap_query(date(2026, 1, 1), date(2026, 12, 31))
        assert query.connector == "OR"


class TestInitialPopulation:
    """Test Initial Population age criteria."""

    @pytest.mark.parametrize("age", [0, 10, 17])
    def test_age_below_18_not_in_population(self, mock_protocol, age):
        """Test patients below age 18 are excluded."""
        patient = Mock()
        assert mock_protocol._in_initial_population(patient, age) is False

    @pytest.mark.parametrize("age", [76, 80, 100])
    def test_age_above_75_not_in_population(self, mock_protocol, age):
        """Test patients above age 75 are excluded."""
        patient = Mock()
        assert mock_protocol._in_initial_population(patient, age) is False


class TestGetTestType:
    """Test _get_test_type method for HbA1c vs GMI detection."""

    def test_returns_hba1c_for_non_gmi_code(self, mock_protocol, mock_lab_report):
        """Test HbA1c is returned when coding doesn't match GMI."""
        mock_lab_value = Mock()
        mock_coding = Mock()
        mock_coding.code = "4548-4"  # HbA1c LOINC code
        mock_lab_value.codings.all.return_value = [mock_coding]
        mock_lab_report.values.first.return_value = mock_lab_value

        assert mock_protocol._get_test_type(mock_lab_report) == "HbA1c"

    def test_returns_gmi_for_gmi_code(self, mock_protocol, mock_lab_report):
        """Test GMI is returned when coding matches GMI LOINC code."""
        mock_lab_value = Mock()
        mock_coding = Mock()
        mock_coding.code = "97506-0"  # GMI LOINC code
        mock_lab_value.codings.all.return_value = [mock_coding]
        mock_lab_report.values.first.return_value = mock_lab_value

        assert mock_protocol._get_test_type(mock_lab_report) == "GMI"

    def test_returns_hba1c_when_no_lab_value(self, mock_protocol, mock_lab_report):
        """Test defaults to HbA1c when no lab value exists."""
        mock_lab_report.values.first.return_value = None

        assert mock_protocol._get_test_type(mock_lab_report) == "HbA1c"


class TestGetGlycemicValue:
    """Test _get_glycemic_value method."""

    def test_extracts_numeric_value(self, mock_protocol, mock_lab_report):
        """Test extraction of numeric glycemic value."""
        mock_lab_value = Mock()
        mock_lab_value.value = 8.5
        mock_lab_report.values.first.return_value = mock_lab_value

        assert mock_protocol._get_glycemic_value(mock_lab_report) == 8.5

    def test_extracts_string_value(self, mock_protocol, mock_lab_report):
        """Test extraction of string glycemic value via relative_float."""
        mock_lab_value = Mock()
        mock_lab_value.value = "9.2"
        mock_lab_report.values.first.return_value = mock_lab_value
        mock_protocol.relative_float = Mock(return_value=9.2)

        assert mock_protocol._get_glycemic_value(mock_lab_report) == 9.2

    def test_returns_none_for_empty_string(self, mock_protocol, mock_lab_report):
        """Test returns None when value is empty string."""
        mock_lab_value = Mock()
        mock_lab_value.value = ""
        mock_lab_report.values.first.return_value = mock_lab_value

        assert mock_protocol._get_glycemic_value(mock_lab_report) is None

    def test_returns_none_for_none_value(self, mock_protocol, mock_lab_report):
        """Test returns None when value is None."""
        mock_lab_value = Mock()
        mock_lab_value.value = None
        mock_lab_report.values.first.return_value = mock_lab_value

        assert mock_protocol._get_glycemic_value(mock_lab_report) is None

    def test_returns_none_when_no_lab_value(self, mock_protocol, mock_lab_report):
        """Test returns None when no lab value exists."""
        mock_lab_report.values.first.return_value = None

        assert mock_protocol._get_glycemic_value(mock_lab_report) is None


# Integration tests for new functionality
def extract_card(effects) -> dict:
    """Return protocol card 'data' from a single effect."""
    assert len(effects) == 1, f"Expected 1 effect, got {len(effects)}"
    eff = effects[0]
    assert eff.type == EffectType.ADD_OR_UPDATE_PROTOCOL_CARD
    import json

    return json.loads(eff.payload)["data"]


def set_patient_context(protocol, patient_id):
    """Set patient context in protocol event."""
    protocol.event.context = {"patient": {"id": str(patient_id)}}


@pytest.fixture
def now():
    """Fixed timestamp for consistent test dates."""
    return arrow.get("2026-12-31T12:00:00Z")


@pytest.fixture
def protocol_instance(now):
    """Create a protocol instance for testing."""
    timeframe_start = arrow.get("2026-01-01T00:00:00Z")
    timeframe_end = now
    protocol = create_protocol_instance(
        CMS122v14DiabetesGlycemicStatusPoorControl,
        timeframe_start=timeframe_start,
        timeframe_end=timeframe_end,
    )
    return protocol


@pytest.fixture
def patient_age_50(now):
    """Patient aged 50 (within 18-75 range)."""
    return PatientFactory.create(birth_date=now.shift(years=-50).date())


@pytest.fixture
def patient_age_70(now):
    """Patient aged 70 (for age 66+ exclusion tests)."""
    return PatientFactory.create(birth_date=now.shift(years=-70).date())


@pytest.fixture
def diabetes_condition_age_50(patient_age_50, now):
    """Create a diabetes condition for patient_age_50."""
    diabetes_codes = list(getattr(Diabetes, "SNOMEDCT", []) or [])
    if not diabetes_codes:
        pytest.skip("Diabetes codes missing")
    return create_condition_with_coding(
        patient_age_50,
        Diabetes,
        onset_date=now.shift(months=-12).date(),
    )


@pytest.fixture
def diabetes_condition_age_70(patient_age_70, now):
    """Create a diabetes condition for patient_age_70."""
    diabetes_codes = list(getattr(Diabetes, "SNOMEDCT", []) or [])
    if not diabetes_codes:
        pytest.skip("Diabetes codes missing")
    return create_condition_with_coding(
        patient_age_70,
        Diabetes,
        onset_date=now.shift(months=-12).date(),
    )


def _create_office_visit_note_type(now, code: str):
    """Helper to create an Office Visit note type."""
    return NoteType.objects.create(
        code=code,
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


@pytest.fixture
def eligible_note(patient_age_50, now):
    """Create an eligible encounter note for patient_age_50."""
    note = NoteFactory.create(
        patient=patient_age_50, datetime_of_service=now.shift(months=-6).datetime
    )
    # Set note type to Office Visit
    office_visit_codes = list(getattr(OfficeVisit, "SNOMEDCT", []) or [])
    if not office_visit_codes:
        office_visit_codes = list(getattr(OfficeVisit, "CPT", []) or [])
    if office_visit_codes:
        note_type = _create_office_visit_note_type(now, office_visit_codes[0])
        note.note_type_version = note_type
        note.save()
    return note


@pytest.fixture
def eligible_note_age_70(patient_age_70, now):
    """Create an eligible encounter note for patient_age_70."""
    note = NoteFactory.create(
        patient=patient_age_70, datetime_of_service=now.shift(months=-6).datetime
    )
    # Set note type to Office Visit
    office_visit_codes = list(getattr(OfficeVisit, "SNOMEDCT", []) or [])
    if not office_visit_codes:
        office_visit_codes = list(getattr(OfficeVisit, "CPT", []) or [])
    if office_visit_codes:
        note_type = _create_office_visit_note_type(now, office_visit_codes[0])
        note.note_type_version = note_type
        note.save()
    return note


class TestHospiceCareExclusion:
    """Test hospice care exclusion logic including inpatient discharge disposition."""

    @pytest.mark.django_db
    def test_inpatient_discharge_to_hospice_excludes(
        self, now, protocol_instance, patient_age_50, diabetes_condition_age_50, eligible_note
    ):
        """Test that inpatient encounter with discharge disposition to hospice excludes patient."""
        # Create inpatient encounter that ends during measurement period
        inpatient_codes = list(getattr(EncounterInpatient, "SNOMEDCT", []) or [])
        if not inpatient_codes:
            pytest.skip("EncounterInpatient codes missing")

        # Create note for inpatient encounter
        inpatient_note = NoteFactory.create(
            patient=patient_age_50,
            datetime_of_service=now.shift(months=-6).datetime,
        )
        note_type = NoteType.objects.create(
            code=inpatient_codes[0],
            system="http://snomed.info/sct",
            display="Inpatient Encounter",
            name="Inpatient Encounter",
            icon="hospital",
            category=NoteTypeCategories.ENCOUNTER,
            rank=1,
            is_default_appointment_type=False,
            is_scheduleable=True,
            is_telehealth=False,
            is_billable=True,
            defer_place_of_service_to_practice_location=False,
            available_places_of_service=[],
            default_place_of_service=PracticeLocationPOS.INPATIENT_HOSPITAL,
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
        inpatient_note.note_type_version = note_type
        inpatient_note.save()

        # Create encounter that ends during measurement period
        EncounterFactory.create(
            note=inpatient_note,
            end_time=now.shift(months=-6).datetime,
        )

        # Create discharge disposition observation linked to the note
        observation = ObservationFactory.create(
            patient=patient_age_50,
            note_id=inpatient_note.dbid,
            effective_datetime=now.shift(months=-6).datetime,
            category="vital-signs",
            units="",
            value="",
            name="Discharge disposition",
        )
        ObservationValueCodingFactory.create(
            observation=observation,
            code="428361000124107",  # Discharge to home for hospice care
            system="http://snomed.info/sct",
            display="Discharge to home for hospice care",
        )

        set_patient_context(protocol_instance, patient_age_50.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == ProtocolCard.Status.NOT_APPLICABLE.value

    @pytest.mark.django_db
    def test_hospice_diagnosis_excludes(
        self, now, protocol_instance, patient_age_50, diabetes_condition_age_50, eligible_note
    ):
        """Test that hospice diagnosis excludes patient."""
        hospice_codes = list(getattr(HospiceDiagnosis, "SNOMEDCT", []) or [])
        if not hospice_codes:
            pytest.skip("HospiceDiagnosis codes missing")

        create_condition_with_coding(
            patient_age_50,
            HospiceDiagnosis,
            onset_date=now.shift(months=-6).date(),
        )

        set_patient_context(protocol_instance, patient_age_50.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == ProtocolCard.Status.NOT_APPLICABLE.value


class TestFrailtyDeviceOrders:
    """Test frailty device orders with date filtering."""

    @pytest.mark.django_db
    def test_frailty_device_order_during_period(
        self, now, protocol_instance, patient_age_70, diabetes_condition_age_70
    ):
        """Test that frailty device order during measurement period is detected."""
        # Get frailty device HCPCS codes
        frailty_device_hcpcs = list(getattr(FrailtyDevice, "HCPCSLEVELII", []) or [])
        if not frailty_device_hcpcs:
            pytest.skip("FrailtyDevice HCPCS codes missing")

        # Create note during measurement period
        note = NoteFactory.create(
            patient=patient_age_70,
            datetime_of_service=now.shift(months=-6).datetime,
        )

        # Create claim with frailty device code (primary check in the method)
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

        # Verify frailty device orders are detected
        assert protocol_instance._has_frailty_device_orders(patient_age_70) is True

    @pytest.mark.django_db
    def test_frailty_device_order_before_period_not_detected(
        self, now, protocol_instance, patient_age_70, diabetes_condition_age_70
    ):
        """Test that frailty device order before measurement period is NOT detected."""
        # Create note before measurement period
        note = NoteFactory.create(
            patient=patient_age_70,
            datetime_of_service=now.shift(years=-2).datetime,  # 2 years ago
        )

        # Create device order linked to the note (Device model doesn't have factory)
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

        # Verify frailty device orders are NOT detected (outside measurement period)
        assert protocol_instance._has_frailty_device_orders(patient_age_70) is False


class TestNursingHomeExclusion:
    """Test nursing home exclusion with 'on or before end' date logic."""

    @pytest.mark.django_db
    def test_nursing_home_encounter_before_period_excludes(
        self,
        now,
        protocol_instance,
        patient_age_70,
        diabetes_condition_age_70,
        eligible_note_age_70,
    ):
        """Test that nursing home encounter before measurement period (but on or before end) excludes patient."""
        # Create nursing facility encounter BEFORE measurement period start
        # but still "on or before end" of measurement period
        nursing_codes = list(getattr(NursingFacilityVisit, "SNOMEDCT", []) or [])
        if not nursing_codes:
            pytest.skip("NursingFacilityVisit codes missing")

        # Create note BEFORE measurement period start
        note = NoteFactory.create(
            patient=patient_age_70,
            datetime_of_service=now.shift(years=-2).datetime,  # 2 years ago (before MP start)
        )
        note_type = NoteType.objects.create(
            code=nursing_codes[0],
            system="http://snomed.info/sct",
            display="Nursing Facility Visit",
            name="Nursing Facility Visit",
            icon="nursing",
            category=NoteTypeCategories.ENCOUNTER,
            rank=1,
            is_default_appointment_type=False,
            is_scheduleable=True,
            is_telehealth=False,
            is_billable=True,
            defer_place_of_service_to_practice_location=False,
            available_places_of_service=[],
            default_place_of_service=PracticeLocationPOS.NURSING,
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

        # Create encounter with start_time before period (but <= end)
        EncounterFactory.create(
            note=note,
            start_time=now.shift(years=-2).datetime,
        )

        set_patient_context(protocol_instance, patient_age_70.id)
        card = extract_card(protocol_instance.compute())

        # Should be excluded because encounter is "on or before end" of measurement period
        assert card["status"] == ProtocolCard.Status.NOT_APPLICABLE.value

    @pytest.mark.django_db
    def test_nursing_home_claim_before_period_excludes(
        self,
        now,
        protocol_instance,
        patient_age_70,
        diabetes_condition_age_70,
        eligible_note_age_70,
    ):
        """Test that nursing home claim before measurement period (but on or before end) excludes patient."""
        nursing_cpt_codes = list(getattr(NursingFacilityVisit, "CPT", []) or [])
        if not nursing_cpt_codes:
            pytest.skip("NursingFacilityVisit CPT codes missing")

        # Create note BEFORE measurement period start
        note = NoteFactory.create(
            patient=patient_age_70,
            datetime_of_service=now.shift(years=-2).datetime,  # 2 years ago
        )

        # Create claim with from_date before period (but <= end)
        claim = ClaimFactory.create(note=note)
        ClaimLineItem.objects.create(
            claim=claim,
            status=ClaimLineItemStatus.ACTIVE,
            charge=100.00,
            from_date=now.shift(years=-2).date().isoformat(),  # Before MP start
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

        set_patient_context(protocol_instance, patient_age_70.id)
        card = extract_card(protocol_instance.compute())

        # Should be excluded because claim is "on or before end" of measurement period
        assert card["status"] == ProtocolCard.Status.NOT_APPLICABLE.value


class TestAdvancedIllnessExclusion:
    """Test advanced illness exclusion with lookback period."""

    @pytest.mark.django_db
    def test_advanced_illness_in_prior_year_excludes(
        self,
        now,
        protocol_instance,
        patient_age_70,
        diabetes_condition_age_70,
        eligible_note_age_70,
    ):
        """Test that advanced illness diagnosis in year before measurement period excludes patient."""
        # Create advanced illness diagnosis in year BEFORE measurement period
        advanced_illness_codes = list(getattr(AdvancedIllness, "SNOMEDCT", []) or [])
        if not advanced_illness_codes:
            pytest.skip("AdvancedIllness codes missing")

        # Create frailty diagnosis first (required for exclusion)
        frailty_codes = list(getattr(FrailtyDiagnosis, "SNOMEDCT", []) or [])
        if not frailty_codes:
            pytest.skip("FrailtyDiagnosis codes missing")

        create_condition_with_coding(
            patient_age_70,
            FrailtyDiagnosis,
            onset_date=now.shift(months=-6).date(),
        )

        # Create advanced illness in year BEFORE measurement period (but within lookback)
        create_condition_with_coding(
            patient_age_70,
            AdvancedIllness,
            onset_date=now.shift(years=-1, months=-6).date(),  # 1.5 years ago (in prior year)
        )

        set_patient_context(protocol_instance, patient_age_70.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == ProtocolCard.Status.NOT_APPLICABLE.value

    @pytest.mark.django_db
    def test_dementia_meds_in_prior_year_excludes(
        self,
        now,
        protocol_instance,
        patient_age_70,
        diabetes_condition_age_70,
        eligible_note_age_70,
    ):
        """Test that dementia medications in year before measurement period excludes patient."""
        # Create frailty diagnosis first (required for exclusion)
        frailty_codes = list(getattr(FrailtyDiagnosis, "SNOMEDCT", []) or [])
        if not frailty_codes:
            pytest.skip("FrailtyDiagnosis codes missing")

        create_condition_with_coding(
            patient_age_70,
            FrailtyDiagnosis,
            onset_date=now.shift(months=-6).date(),
        )

        # Create dementia medication in year BEFORE measurement period
        dementia_med_codes = list(getattr(DementiaMedications, "RXNORM", []) or [])
        if not dementia_med_codes:
            pytest.skip("DementiaMedications codes missing")

        create_medication_with_coding(
            patient_age_70,
            dementia_med_codes[0],
            "http://www.nlm.nih.gov/research/umls/rxnorm",
            start_date=now.shift(years=-1, months=-6).date(),  # 1.5 years ago
            display="Dementia Medication",
        )

        set_patient_context(protocol_instance, patient_age_70.id)
        card = extract_card(protocol_instance.compute())

        assert card["status"] == ProtocolCard.Status.NOT_APPLICABLE.value
