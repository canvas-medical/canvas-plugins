"""Tests for CMS138v14 Tobacco Use Screening and Cessation Intervention Protocol."""

from datetime import date, datetime
from unittest.mock import MagicMock, Mock, patch

import arrow
import pytest
from cms138v14_preventive_care_and_screening_tobacco_use_screening_and_cessation_intervention.protocols.cms138v14_protocol import (
    CMS138v14TobaccoScreening,
    PopulationResult,
    ScreeningData,
)

from canvas_sdk.events import EventType
from canvas_sdk.v1.data import Patient
from canvas_sdk.v1.data.condition import Condition


@pytest.fixture
def mock_patient() -> Mock:
    """Create a mock patient aged 30 (within age criteria)."""
    patient = Mock(spec=Patient)
    patient.id = "patient-123"
    patient.first_name = "John"
    patient.last_name = "Doe"
    patient.birth_date = "1994-01-01"

    def age_at(dt: datetime | date | arrow.Arrow | str) -> int:
        birth = arrow.get("1994-01-01")
        target = dt if isinstance(dt, arrow.Arrow) else arrow.get(dt)
        age = target.year - birth.year
        if (target.month, target.day) < (birth.month, birth.day):
            age -= 1
        return age

    patient.age_at = Mock(side_effect=age_at)
    return patient


@pytest.fixture
def mock_patient_child() -> Mock:
    """Create a mock patient aged 10 (below age criteria)."""
    patient = Mock(spec=Patient)
    patient.id = "patient-child"
    patient.first_name = "Jimmy"
    patient.last_name = "Doe"
    patient.birth_date = "2014-01-01"

    def age_at(dt: datetime | date | arrow.Arrow | str) -> int:
        birth = arrow.get("2014-01-01")
        target = dt if isinstance(dt, arrow.Arrow) else arrow.get(dt)
        age = target.year - birth.year
        if (target.month, target.day) < (birth.month, birth.day):
            age -= 1
        return age

    patient.age_at = Mock(side_effect=age_at)
    return patient


@pytest.fixture
def mock_patient_teen() -> Mock:
    """Create a mock patient aged 14 (within v14 age criteria >= 12)."""
    patient = Mock(spec=Patient)
    patient.id = "patient-teen"
    patient.first_name = "Jane"
    patient.last_name = "Doe"
    patient.birth_date = "2010-01-01"

    def age_at(dt: datetime | date | arrow.Arrow | str) -> int:
        birth = arrow.get("2010-01-01")
        target = dt if isinstance(dt, arrow.Arrow) else arrow.get(dt)
        age = target.year - birth.year
        if (target.month, target.day) < (birth.month, birth.day):
            age -= 1
        return age

    patient.age_at = Mock(side_effect=age_at)
    return patient


@pytest.fixture
def mock_condition() -> Mock:
    """Create a mock condition."""
    condition = Mock(spec=Condition)
    condition.id = "condition-123"
    condition.entered_in_error = None
    return condition


@pytest.fixture
def mock_event_patient_created() -> Mock:
    """Create a mock PATIENT_CREATED event."""
    event = Mock()
    event.type = EventType.PATIENT_CREATED
    event.target = Mock()
    event.target.id = "patient-123"
    event.context = {"patient": {"id": "patient-123"}}
    return event


@pytest.fixture
def mock_event_condition_created() -> Mock:
    """Create a mock CONDITION_CREATED event."""
    event = Mock()
    event.type = EventType.CONDITION_CREATED
    event.target = Mock()
    event.target.id = "condition-123"
    event.context = {}
    return event


@pytest.fixture
def mock_event_interview_created() -> Mock:
    """Create a mock INTERVIEW_CREATED event."""
    event = Mock()
    event.type = EventType.INTERVIEW_CREATED
    event.target = Mock()
    event.target.id = "interview-123"
    event.context = {"patient": {"id": "patient-123"}}
    return event


@pytest.fixture
def protocol_instance(mock_event_patient_created: Mock) -> CMS138v14TobaccoScreening:
    """Create a protocol instance with mocked dependencies."""
    protocol = CMS138v14TobaccoScreening(mock_event_patient_created)
    return protocol


class TestScreeningData:
    """Tests for the ScreeningData class."""

    def test_init_defaults(self) -> None:
        """Test ScreeningData initializes with None values."""
        data = ScreeningData()
        assert data.most_recent_user is None
        assert data.most_recent_non_user is None
        assert data.counseling_date is None
        assert data.pharmacotherapy_date is None

    def test_has_screening_false_when_no_data(self) -> None:
        """Test has_screening returns False when no screening data."""
        data = ScreeningData()
        assert data.has_screening() is False

    def test_has_screening_true_with_user(self) -> None:
        """Test has_screening returns True when tobacco user screening exists."""
        data = ScreeningData()
        data.most_recent_user = arrow.get("2024-06-01")
        assert data.has_screening() is True

    def test_has_screening_true_with_non_user(self) -> None:
        """Test has_screening returns True when non-user screening exists."""
        data = ScreeningData()
        data.most_recent_non_user = arrow.get("2024-06-01")
        assert data.has_screening() is True

    def test_has_screening_false_when_only_date(self) -> None:
        """Test has_screening returns True when user date exists (old interface)."""
        data = ScreeningData()
        data.most_recent_user = arrow.get("2024-06-01")
        # With old interface, having a date means has_screening is True
        assert data.has_screening() is True

    def test_is_tobacco_user_false_when_no_screening(self) -> None:
        """Test is_tobacco_user returns False when no screening."""
        data = ScreeningData()
        assert data.is_tobacco_user() is False

    def test_is_tobacco_user_false_when_non_user(self) -> None:
        """Test is_tobacco_user returns False when screening shows non-user."""
        data = ScreeningData()
        data.most_recent_non_user = arrow.get("2024-06-01")
        assert data.is_tobacco_user() is False

    def test_is_tobacco_user_true_when_user(self) -> None:
        """Test is_tobacco_user returns True when screening shows user."""
        data = ScreeningData()
        data.most_recent_user = arrow.get("2024-06-01")
        assert data.is_tobacco_user() is True

    def test_is_tobacco_non_user_true(self) -> None:
        """Test is_tobacco_non_user returns True when screening shows non-user."""
        data = ScreeningData()
        data.most_recent_non_user = arrow.get("2024-06-01")
        assert data.is_tobacco_non_user() is True

    def test_is_tobacco_non_user_false_when_user(self) -> None:
        """Test is_tobacco_non_user returns False when screening shows user."""
        data = ScreeningData()
        data.most_recent_user = arrow.get("2024-06-01")
        assert data.is_tobacco_non_user() is False

    def test_is_tobacco_user_uses_most_recent(self) -> None:
        """Test is_tobacco_user compares dates when both exist."""
        data = ScreeningData()
        # User screening is more recent
        data.most_recent_user = arrow.get("2024-07-01")
        data.most_recent_non_user = arrow.get("2024-06-01")
        assert data.is_tobacco_user() is True

        # Non-user screening is more recent
        data.most_recent_user = arrow.get("2024-05-01")
        data.most_recent_non_user = arrow.get("2024-06-01")
        assert data.is_tobacco_user() is False

    def test_has_intervention_false_when_no_data(self) -> None:
        """Test has_intervention returns False when no intervention data."""
        data = ScreeningData()
        assert data.has_intervention() is False

    def test_has_intervention_true_with_counseling(self) -> None:
        """Test has_intervention returns True when counseling exists."""
        data = ScreeningData()
        data.counseling_date = arrow.get("2024-06-01")
        assert data.has_intervention() is True

    def test_has_intervention_true_with_pharmacotherapy(self) -> None:
        """Test has_intervention returns True when pharmacotherapy exists."""
        data = ScreeningData()
        data.pharmacotherapy_date = arrow.get("2024-06-01")
        assert data.has_intervention() is True

    def test_has_intervention_true_with_both(self) -> None:
        """Test has_intervention returns True when both interventions exist."""
        data = ScreeningData()
        data.counseling_date = arrow.get("2024-05-01")
        data.pharmacotherapy_date = arrow.get("2024-06-01")
        assert data.has_intervention() is True


class TestPopulationResult:
    """Tests for the PopulationResult class."""

    def test_init_defaults(self) -> None:
        """Test PopulationResult initializes with correct defaults."""
        result = PopulationResult()
        assert result.in_initial_population is False
        assert result.in_denominator is False
        assert result.in_numerator is False


class TestProtocolInitialization:
    """Tests for protocol initialization."""

    def test_populations_initialized(self, protocol_instance: CMS138v14TobaccoScreening) -> None:
        """Test that populations dictionary is initialized."""
        assert CMS138v14TobaccoScreening.POPULATION_1 in protocol_instance._populations
        assert CMS138v14TobaccoScreening.POPULATION_2 in protocol_instance._populations
        assert CMS138v14TobaccoScreening.POPULATION_3 in protocol_instance._populations

    def test_meta_attributes(self) -> None:
        """Test protocol meta attributes are set correctly."""
        assert (
            CMS138v14TobaccoScreening.Meta.title
            == "Preventive Care and Screening: Tobacco Use: Screening and Cessation Intervention"
        )
        assert "CMS138v14" in CMS138v14TobaccoScreening.Meta.identifiers
        assert CMS138v14TobaccoScreening.Meta.version == "v14.0.0"

    def test_responds_to_events(self) -> None:
        """Test protocol responds to expected events."""
        assert EventType.Name(EventType.PATIENT_CREATED) in CMS138v14TobaccoScreening.RESPONDS_TO
        assert EventType.Name(EventType.INTERVIEW_CREATED) in CMS138v14TobaccoScreening.RESPONDS_TO
        assert EventType.Name(EventType.CONDITION_CREATED) in CMS138v14TobaccoScreening.RESPONDS_TO


class TestGetPatient:
    """Tests for _get_patient method."""

    @patch("canvas_sdk.v1.data.Patient.objects")
    def test_get_patient_from_patient_event(
        self,
        mock_patient_objects: MagicMock,
        mock_event_patient_created: Mock,
        mock_patient: Mock,
    ) -> None:
        """Test getting patient from PATIENT_CREATED event."""
        mock_patient_objects.filter.return_value.first.return_value = mock_patient

        protocol = CMS138v14TobaccoScreening(mock_event_patient_created)
        patient = protocol._get_patient()

        assert patient == mock_patient
        mock_patient_objects.filter.assert_called_once_with(id="patient-123")

    @patch("canvas_sdk.v1.data.condition.Condition.objects")
    def test_get_patient_from_condition_event(
        self,
        mock_condition_objects: MagicMock,
        mock_event_condition_created: Mock,
        mock_patient: Mock,
    ) -> None:
        """Test getting patient from CONDITION_CREATED event."""
        mock_condition = Mock()
        mock_condition.patient = mock_patient
        mock_condition_objects.filter.return_value.select_related.return_value.first.return_value = mock_condition

        protocol = CMS138v14TobaccoScreening(mock_event_condition_created)
        patient = protocol._get_patient()

        assert patient == mock_patient

    @patch("canvas_sdk.v1.data.condition.Condition.objects")
    def test_get_patient_returns_none_when_condition_not_found(
        self,
        mock_condition_objects: MagicMock,
        mock_event_condition_created: Mock,
    ) -> None:
        """Test returns None when condition not found."""
        mock_condition_objects.filter.return_value.select_related.return_value.first.return_value = None

        protocol = CMS138v14TobaccoScreening(mock_event_condition_created)
        patient = protocol._get_patient()

        assert patient is None


class TestIsChartContext:
    """Tests for _is_chart_context method."""

    def test_chart_context_true_for_patient_created(self, mock_event_patient_created: Mock) -> None:
        """Test _is_chart_context returns True for PATIENT_CREATED event."""
        protocol = CMS138v14TobaccoScreening(mock_event_patient_created)
        assert protocol._is_chart_context() is True

    def test_chart_context_true_for_patient_updated(self) -> None:
        """Test _is_chart_context returns True for PATIENT_UPDATED event."""
        event = Mock()
        event.type = EventType.PATIENT_UPDATED
        event.target = Mock()
        event.target.id = "patient-123"
        event.context = {}

        protocol = CMS138v14TobaccoScreening(event)
        assert protocol._is_chart_context() is True

    def test_chart_context_true_when_patient_in_context(
        self, mock_event_interview_created: Mock
    ) -> None:
        """Test _is_chart_context returns True when patient in event context."""
        protocol = CMS138v14TobaccoScreening(mock_event_interview_created)
        assert protocol._is_chart_context() is True

    def test_chart_context_false_when_no_patient_context(self) -> None:
        """Test _is_chart_context returns False when no patient in context."""
        event = Mock()
        event.type = EventType.CLAIM_CREATED
        event.target = Mock()
        event.target.id = "claim-123"
        event.context = {}

        protocol = CMS138v14TobaccoScreening(event)
        assert protocol._is_chart_context() is False


class TestInInitialPopulation:
    """Tests for _in_initial_population method."""

    def test_not_in_population_no_birth_date(
        self, protocol_instance: CMS138v14TobaccoScreening
    ) -> None:
        """Test patient without birth date is not in initial population."""
        patient = Mock(spec=Patient)
        patient.first_name = "Test"
        patient.birth_date = None

        in_pop = protocol_instance._in_initial_population(patient)

        assert in_pop is False

    def test_not_in_population_age_under_12(
        self,
        protocol_instance: CMS138v14TobaccoScreening,
        mock_patient_child: Mock,
    ) -> None:
        """Test patient under 12 is not in initial population."""
        in_pop = protocol_instance._in_initial_population(mock_patient_child)

        assert in_pop is False

    def test_in_population_age_12_plus_chart_context(
        self,
        mock_event_patient_created: Mock,
        mock_patient_teen: Mock,
    ) -> None:
        """Test patient 12+ in chart context is in initial population."""
        protocol = CMS138v14TobaccoScreening(mock_event_patient_created)

        in_pop = protocol._in_initial_population(mock_patient_teen)

        assert in_pop is True

    @patch.object(CMS138v14TobaccoScreening, "_is_chart_context")
    @patch.object(CMS138v14TobaccoScreening, "_count_qualifying_visits")
    @patch.object(CMS138v14TobaccoScreening, "_count_preventive_visits")
    def test_in_population_with_qualifying_visits(
        self,
        mock_preventive: MagicMock,
        mock_qualifying: MagicMock,
        mock_chart_context: MagicMock,
        protocol_instance: CMS138v14TobaccoScreening,
        mock_patient: Mock,
    ) -> None:
        """Test patient with 2+ qualifying visits is in initial population."""
        mock_chart_context.return_value = False
        mock_qualifying.return_value = 2
        mock_preventive.return_value = 0

        in_pop = protocol_instance._in_initial_population(mock_patient)

        assert in_pop is True

    @patch.object(CMS138v14TobaccoScreening, "_is_chart_context")
    @patch.object(CMS138v14TobaccoScreening, "_count_qualifying_visits")
    @patch.object(CMS138v14TobaccoScreening, "_count_preventive_visits")
    def test_in_population_with_preventive_visit(
        self,
        mock_preventive: MagicMock,
        mock_qualifying: MagicMock,
        mock_chart_context: MagicMock,
        protocol_instance: CMS138v14TobaccoScreening,
        mock_patient: Mock,
    ) -> None:
        """Test patient with 1+ preventive visit is in initial population."""
        mock_chart_context.return_value = False
        mock_qualifying.return_value = 0
        mock_preventive.return_value = 1

        in_pop = protocol_instance._in_initial_population(mock_patient)

        assert in_pop is True

    @patch.object(CMS138v14TobaccoScreening, "_is_chart_context")
    @patch.object(CMS138v14TobaccoScreening, "_count_qualifying_visits")
    @patch.object(CMS138v14TobaccoScreening, "_count_preventive_visits")
    def test_not_in_population_insufficient_visits(
        self,
        mock_preventive: MagicMock,
        mock_qualifying: MagicMock,
        mock_chart_context: MagicMock,
        protocol_instance: CMS138v14TobaccoScreening,
        mock_patient: Mock,
    ) -> None:
        """Test patient with insufficient visits is not in initial population."""
        mock_chart_context.return_value = False
        mock_qualifying.return_value = 1
        mock_preventive.return_value = 0

        in_pop = protocol_instance._in_initial_population(mock_patient)

        assert in_pop is False


class TestCountQualifyingVisits:
    """Tests for _count_qualifying_visits method."""

    @patch("canvas_sdk.v1.data.claim_line_item.ClaimLineItem.objects")
    @patch("canvas_sdk.v1.data.encounter.Encounter.objects")
    def test_count_qualifying_visits_from_encounters(
        self,
        mock_encounter_objects: MagicMock,
        mock_claim_objects: MagicMock,
        protocol_instance: CMS138v14TobaccoScreening,
        mock_patient: Mock,
    ) -> None:
        """Test counting qualifying visits from Encounter model."""
        # Mock encounters returning 3 distinct note IDs
        mock_encounter_objects.filter.return_value.values_list.return_value = [
            "note-1",
            "note-2",
            "note-3",
        ]
        # No claims
        mock_claim_objects.filter.return_value.values_list.return_value = []

        count = protocol_instance._count_qualifying_visits(mock_patient)

        assert count == 3

    @patch("canvas_sdk.v1.data.claim_line_item.ClaimLineItem.objects")
    @patch("canvas_sdk.v1.data.encounter.Encounter.objects")
    def test_count_qualifying_visits_from_claims(
        self,
        mock_encounter_objects: MagicMock,
        mock_claim_objects: MagicMock,
        protocol_instance: CMS138v14TobaccoScreening,
        mock_patient: Mock,
    ) -> None:
        """Test counting qualifying visits from ClaimLineItem model."""
        # No encounters
        mock_encounter_objects.filter.return_value.values_list.return_value = []
        # Mock claims returning 2 distinct note IDs
        mock_claim_objects.filter.return_value.values_list.return_value = ["note-1", "note-2"]

        count = protocol_instance._count_qualifying_visits(mock_patient)

        assert count == 2

    @patch("canvas_sdk.v1.data.claim_line_item.ClaimLineItem.objects")
    @patch("canvas_sdk.v1.data.encounter.Encounter.objects")
    def test_count_qualifying_visits_combined(
        self,
        mock_encounter_objects: MagicMock,
        mock_claim_objects: MagicMock,
        protocol_instance: CMS138v14TobaccoScreening,
        mock_patient: Mock,
    ) -> None:
        """Test counting qualifying visits combines encounters and claims (distinct note IDs)."""
        # Mock encounter returning 1 note ID
        mock_encounter_objects.filter.return_value.values_list.return_value = ["note-1"]
        # Mock claim returning a DIFFERENT note ID (so both count)
        mock_claim_objects.filter.return_value.values_list.return_value = ["note-2"]

        count = protocol_instance._count_qualifying_visits(mock_patient)

        assert count == 2

    @patch("canvas_sdk.v1.data.claim_line_item.ClaimLineItem.objects")
    @patch("canvas_sdk.v1.data.encounter.Encounter.objects")
    def test_count_qualifying_visits_deduplicates_same_note(
        self,
        mock_encounter_objects: MagicMock,
        mock_claim_objects: MagicMock,
        protocol_instance: CMS138v14TobaccoScreening,
        mock_patient: Mock,
    ) -> None:
        """Test that visits from same note are not double-counted."""
        # Mock encounter and claim returning SAME note ID
        mock_encounter_objects.filter.return_value.values_list.return_value = ["note-1"]
        mock_claim_objects.filter.return_value.values_list.return_value = ["note-1"]

        count = protocol_instance._count_qualifying_visits(mock_patient)

        # Should only count once
        assert count == 1


class TestCountPreventiveVisits:
    """Tests for _count_preventive_visits method."""

    @patch("canvas_sdk.v1.data.claim_line_item.ClaimLineItem.objects")
    @patch("canvas_sdk.v1.data.encounter.Encounter.objects")
    def test_count_preventive_visits_from_encounters(
        self,
        mock_encounter_objects: MagicMock,
        mock_claim_objects: MagicMock,
        protocol_instance: CMS138v14TobaccoScreening,
        mock_patient: Mock,
    ) -> None:
        """Test counting preventive visits from Encounter model."""
        # Mock encounter returning 1 note ID
        mock_encounter_objects.filter.return_value.values_list.return_value = ["note-1"]
        # No claims
        mock_claim_objects.filter.return_value.values_list.return_value = []

        count = protocol_instance._count_preventive_visits(mock_patient)

        assert count == 1

    @patch("canvas_sdk.v1.data.claim_line_item.ClaimLineItem.objects")
    @patch("canvas_sdk.v1.data.encounter.Encounter.objects")
    def test_count_preventive_visits_from_claims(
        self,
        mock_encounter_objects: MagicMock,
        mock_claim_objects: MagicMock,
        protocol_instance: CMS138v14TobaccoScreening,
        mock_patient: Mock,
    ) -> None:
        """Test counting preventive visits from ClaimLineItem model."""
        # No encounters
        mock_encounter_objects.filter.return_value.values_list.return_value = []
        # Mock claim returning 1 note ID
        mock_claim_objects.filter.return_value.values_list.return_value = ["note-1"]

        count = protocol_instance._count_preventive_visits(mock_patient)

        assert count == 1

    @patch("canvas_sdk.v1.data.claim_line_item.ClaimLineItem.objects")
    @patch("canvas_sdk.v1.data.encounter.Encounter.objects")
    def test_count_preventive_visits_deduplicates_same_note(
        self,
        mock_encounter_objects: MagicMock,
        mock_claim_objects: MagicMock,
        protocol_instance: CMS138v14TobaccoScreening,
        mock_patient: Mock,
    ) -> None:
        """Test that preventive visits from same note are not double-counted."""
        # Mock encounter and claim returning SAME note ID
        mock_encounter_objects.filter.return_value.values_list.return_value = ["note-1"]
        mock_claim_objects.filter.return_value.values_list.return_value = ["note-1"]

        count = protocol_instance._count_preventive_visits(mock_patient)

        # Should only count once
        assert count == 1


class TestHasHospiceCareInPeriod:
    """Tests for _has_hospice_care_in_period method."""

    @patch("canvas_sdk.v1.data.condition.Condition.objects")
    def test_has_hospice_diagnosis(
        self,
        mock_condition_objects: MagicMock,
        protocol_instance: CMS138v14TobaccoScreening,
        mock_patient: Mock,
    ) -> None:
        """Test returns True when hospice diagnosis exists."""
        mock_condition_objects.for_patient.return_value.find.return_value.committed.return_value.filter.return_value.filter.return_value.exists.return_value = True

        result = protocol_instance._has_hospice_care_in_period(mock_patient)

        assert result is True

    @patch("canvas_sdk.v1.data.claim_line_item.ClaimLineItem.objects")
    @patch("canvas_sdk.v1.data.Observation.objects")
    @patch("canvas_sdk.v1.data.encounter.Encounter.objects")
    @patch("canvas_sdk.v1.data.condition.Condition.objects")
    def test_no_hospice_care(
        self,
        mock_condition_objects: MagicMock,
        mock_encounter_objects: MagicMock,
        mock_observation_objects: MagicMock,
        mock_claim_objects: MagicMock,
        protocol_instance: CMS138v14TobaccoScreening,
        mock_patient: Mock,
    ) -> None:
        """Test returns False when no hospice care indicators."""
        # Condition query now has two .filter() calls: entered_in_error_id and overlap_query
        mock_condition_objects.for_patient.return_value.find.return_value.committed.return_value.filter.return_value.filter.return_value.exists.return_value = False
        mock_encounter_objects.filter.return_value.exists.return_value = False
        mock_encounter_objects.filter.return_value.values_list.return_value = []
        # Observation queries now use .committed() before .filter()
        mock_observation_objects.for_patient.return_value.committed.return_value.filter.return_value.exists.return_value = False
        mock_claim_objects.filter.return_value.exists.return_value = False

        result = protocol_instance._has_hospice_care_in_period(mock_patient)

        assert result is False


class TestCheckInterviewResponses:
    """Tests for _check_interview_responses method.

    Note: The implementation now validates BOTH the question code (TobaccoUseScreening LOINC)
    and the answer code (TobaccoUser/TobaccoNonUser SNOMED) per CMS spec.
    """

    @patch("canvas_sdk.v1.data.questionnaire.InterviewQuestionResponse.objects")
    def test_finds_tobacco_user_response(
        self,
        mock_interview_objects: MagicMock,
        protocol_instance: CMS138v14TobaccoScreening,
        mock_patient: Mock,
    ) -> None:
        """Test finds tobacco user response from interview."""
        mock_interview = Mock()
        mock_interview.created = datetime(2024, 6, 15, 10, 0, 0)

        mock_response_option = Mock()
        mock_response_option.code = "449868002"  # Tobacco user code

        mock_response = Mock()
        mock_response.interview = mock_interview
        mock_response.response_option = mock_response_option

        # Mock the single query that gets the most recent screening
        mock_interview_objects.filter.return_value.select_related.return_value.order_by.return_value.first.return_value = mock_response

        result = ScreeningData()
        tobacco_user_codes = {"449868002"}
        tobacco_non_user_codes = {"266919005"}

        protocol_instance._check_interview_responses(
            mock_patient, result, tobacco_user_codes, tobacco_non_user_codes
        )

        assert result.most_recent_user is not None
        assert result.is_tobacco_user() is True

    @patch("canvas_sdk.v1.data.questionnaire.InterviewQuestionResponse.objects")
    def test_finds_tobacco_non_user_response(
        self,
        mock_interview_objects: MagicMock,
        protocol_instance: CMS138v14TobaccoScreening,
        mock_patient: Mock,
    ) -> None:
        """Test finds tobacco non-user response from interview."""
        mock_interview = Mock()
        mock_interview.created = datetime(2024, 6, 15, 10, 0, 0)

        mock_response_option = Mock()
        mock_response_option.code = "266919005"  # Non-user code

        mock_response = Mock()
        mock_response.interview = mock_interview
        mock_response.response_option = mock_response_option

        # Mock the single query that gets the most recent screening
        mock_interview_objects.filter.return_value.select_related.return_value.order_by.return_value.first.return_value = mock_response

        result = ScreeningData()
        tobacco_user_codes = {"449868002"}
        tobacco_non_user_codes = {"266919005"}

        protocol_instance._check_interview_responses(
            mock_patient, result, tobacco_user_codes, tobacco_non_user_codes
        )

        assert result.most_recent_non_user is not None
        assert result.is_tobacco_non_user() is True

    @patch("canvas_sdk.v1.data.questionnaire.InterviewQuestionResponse.objects")
    def test_most_recent_screening_determines_status(
        self,
        mock_interview_objects: MagicMock,
        protocol_instance: CMS138v14TobaccoScreening,
        mock_patient: Mock,
    ) -> None:
        """Test that the most recent screening result determines user/non-user status.

        Per CMS138v14 spec: Get the MOST RECENT screening, then check its result.
        The implementation uses a single query that returns the most recent response.
        """
        # The most recent screening shows tobacco user
        mock_interview = Mock()
        mock_interview.created = datetime(2024, 7, 15, 10, 0, 0)

        mock_response_option = Mock()
        mock_response_option.code = "449868002"  # Tobacco user code

        mock_response = Mock()
        mock_response.interview = mock_interview
        mock_response.response_option = mock_response_option

        # Mock returns only the most recent response (ordered by -interview__created)
        mock_interview_objects.filter.return_value.select_related.return_value.order_by.return_value.first.return_value = mock_response

        result = ScreeningData()
        tobacco_user_codes = {"449868002"}
        tobacco_non_user_codes = {"266919005"}

        protocol_instance._check_interview_responses(
            mock_patient, result, tobacco_user_codes, tobacco_non_user_codes
        )

        # Only the most recent result is set
        assert result.most_recent_user is not None
        assert result.most_recent_non_user is None
        assert result.is_tobacco_user() is True


class TestComputePopulations:
    """Tests for _compute_populations method."""

    def test_population_1_no_screening(self, protocol_instance: CMS138v14TobaccoScreening) -> None:
        """Test Population 1 numerator is False when no screening."""
        data = ScreeningData()

        protocol_instance._compute_populations(data)

        pop1 = protocol_instance._populations[CMS138v14TobaccoScreening.POPULATION_1]
        assert pop1.in_numerator is False

    def test_population_1_has_screening(self, protocol_instance: CMS138v14TobaccoScreening) -> None:
        """Test Population 1 numerator is True when screened."""
        data = ScreeningData()
        data.most_recent_non_user = arrow.get("2024-06-01")

        protocol_instance._compute_populations(data)

        pop1 = protocol_instance._populations[CMS138v14TobaccoScreening.POPULATION_1]
        assert pop1.in_numerator is True

    def test_population_2_not_tobacco_user(
        self, protocol_instance: CMS138v14TobaccoScreening
    ) -> None:
        """Test Population 2 denominator is False when not tobacco user."""
        data = ScreeningData()
        data.most_recent_non_user = arrow.get("2024-06-01")

        protocol_instance._compute_populations(data)

        pop2 = protocol_instance._populations[CMS138v14TobaccoScreening.POPULATION_2]
        assert pop2.in_denominator is False
        assert pop2.in_numerator is False  # Explicit False when not in denominator

    def test_population_2_no_screening(self, protocol_instance: CMS138v14TobaccoScreening) -> None:
        """Test Population 2 denominator is False when no screening performed."""
        data = ScreeningData()
        # No most_recent_user or most_recent_non_user set

        protocol_instance._compute_populations(data)

        pop2 = protocol_instance._populations[CMS138v14TobaccoScreening.POPULATION_2]
        assert pop2.in_denominator is False
        assert pop2.in_numerator is False

    def test_population_2_tobacco_user_no_intervention(
        self, protocol_instance: CMS138v14TobaccoScreening
    ) -> None:
        """Test Population 2 numerator is False when tobacco user without intervention."""
        data = ScreeningData()
        data.most_recent_user = arrow.get("2024-06-01")

        protocol_instance._compute_populations(data)

        pop2 = protocol_instance._populations[CMS138v14TobaccoScreening.POPULATION_2]
        assert pop2.in_denominator is True
        assert pop2.in_numerator is False

    def test_population_2_tobacco_user_with_intervention(
        self, protocol_instance: CMS138v14TobaccoScreening
    ) -> None:
        """Test Population 2 numerator is True when tobacco user has intervention."""
        data = ScreeningData()
        data.most_recent_user = arrow.get("2024-06-01")
        data.counseling_date = arrow.get("2024-07-01")

        protocol_instance._compute_populations(data)

        pop2 = protocol_instance._populations[CMS138v14TobaccoScreening.POPULATION_2]
        assert pop2.in_numerator is True

    def test_population_3_non_user_screened(
        self, protocol_instance: CMS138v14TobaccoScreening
    ) -> None:
        """Test Population 3 numerator is True for screened non-user."""
        data = ScreeningData()
        data.most_recent_non_user = arrow.get("2024-06-01")

        protocol_instance._compute_populations(data)

        pop3 = protocol_instance._populations[CMS138v14TobaccoScreening.POPULATION_3]
        assert pop3.in_numerator is True

    def test_population_3_user_without_intervention(
        self, protocol_instance: CMS138v14TobaccoScreening
    ) -> None:
        """Test Population 3 numerator is False for tobacco user without intervention."""
        data = ScreeningData()
        data.most_recent_user = arrow.get("2024-06-01")

        protocol_instance._compute_populations(data)

        pop3 = protocol_instance._populations[CMS138v14TobaccoScreening.POPULATION_3]
        assert pop3.in_numerator is False

    def test_population_3_user_with_intervention(
        self, protocol_instance: CMS138v14TobaccoScreening
    ) -> None:
        """Test Population 3 numerator is True for tobacco user with intervention."""
        data = ScreeningData()
        data.most_recent_user = arrow.get("2024-06-01")
        data.pharmacotherapy_date = arrow.get("2024-07-01")

        protocol_instance._compute_populations(data)

        pop3 = protocol_instance._populations[CMS138v14TobaccoScreening.POPULATION_3]
        assert pop3.in_numerator is True


class TestGetValueSetCodes:
    """Tests for _get_value_set_codes method."""

    def test_get_single_attribute(self, protocol_instance: CMS138v14TobaccoScreening) -> None:
        """Test getting codes from single attribute."""

        class MockValueSet:
            SNOMEDCT = {"code1", "code2"}

        codes = protocol_instance._get_value_set_codes(MockValueSet, "SNOMEDCT")

        assert codes == {"code1", "code2"}

    def test_get_multiple_attributes(self, protocol_instance: CMS138v14TobaccoScreening) -> None:
        """Test getting codes from multiple attributes."""

        class MockValueSet:
            SNOMEDCT = {"snomed1"}
            CPT = {"cpt1", "cpt2"}

        codes = protocol_instance._get_value_set_codes(MockValueSet, "SNOMEDCT", "CPT")

        assert codes == {"snomed1", "cpt1", "cpt2"}

    def test_get_missing_attribute(self, protocol_instance: CMS138v14TobaccoScreening) -> None:
        """Test returns empty set for missing attribute."""

        class MockValueSet:
            SNOMEDCT = {"code1"}

        codes = protocol_instance._get_value_set_codes(MockValueSet, "ICD10CM")

        assert codes == set()


class TestProtocolCardCreation:
    """Tests for protocol card creation methods."""

    def test_create_not_applicable_card(
        self, protocol_instance: CMS138v14TobaccoScreening, mock_patient: Mock
    ) -> None:
        """Test creating NOT_APPLICABLE card."""
        effect = protocol_instance._create_not_applicable_card(mock_patient)

        assert effect is not None

    def test_create_satisfied_card_non_user(
        self, protocol_instance: CMS138v14TobaccoScreening, mock_patient: Mock
    ) -> None:
        """Test creating SATISFIED card for non-user."""
        data = ScreeningData()
        data.most_recent_non_user = arrow.get("2024-06-15")

        effect = protocol_instance._create_satisfied_card(mock_patient, data)

        assert effect is not None

    def test_create_satisfied_card_user_with_intervention(
        self, protocol_instance: CMS138v14TobaccoScreening, mock_patient: Mock
    ) -> None:
        """Test creating SATISFIED card for user with intervention."""
        data = ScreeningData()
        data.most_recent_user = arrow.get("2024-06-15")
        data.counseling_date = arrow.get("2024-07-01")

        effect = protocol_instance._create_satisfied_card(mock_patient, data)

        assert effect is not None

    @patch("canvas_sdk.v1.data.Questionnaire.objects")
    def test_create_due_card_for_screening(
        self,
        mock_questionnaire_objects: MagicMock,
        protocol_instance: CMS138v14TobaccoScreening,
        mock_patient: Mock,
    ) -> None:
        """Test creating DUE card for screening (no screening data)."""
        # Mock questionnaire lookup to avoid database access
        mock_questionnaire = Mock()
        mock_questionnaire.questions.all.return_value = []
        mock_questionnaire_objects.get.return_value = mock_questionnaire

        data = ScreeningData()  # No screening
        effect = protocol_instance._create_due_card(mock_patient, data)

        assert effect is not None

    def test_create_due_card_for_intervention(
        self, protocol_instance: CMS138v14TobaccoScreening, mock_patient: Mock
    ) -> None:
        """Test creating DUE card for intervention (tobacco user without intervention)."""
        data = ScreeningData()
        data.most_recent_user = arrow.get("2024-06-15")  # Tobacco user
        effect = protocol_instance._create_due_card(mock_patient, data)

        assert effect is not None


class TestComputeMethod:
    """Integration tests for compute method."""

    @patch.object(CMS138v14TobaccoScreening, "_get_patient")
    def test_compute_returns_empty_when_no_patient(
        self,
        mock_get_patient: MagicMock,
        protocol_instance: CMS138v14TobaccoScreening,
    ) -> None:
        """Test compute returns empty list when patient not found."""
        mock_get_patient.return_value = None

        effects = protocol_instance.compute()

        assert effects == []

    @patch.object(CMS138v14TobaccoScreening, "_create_not_applicable_card")
    @patch.object(CMS138v14TobaccoScreening, "_in_initial_population")
    @patch.object(CMS138v14TobaccoScreening, "_get_patient")
    def test_compute_not_applicable_for_excluded_patient(
        self,
        mock_get_patient: MagicMock,
        mock_in_initial_pop: MagicMock,
        mock_create_card: MagicMock,
        protocol_instance: CMS138v14TobaccoScreening,
        mock_patient: Mock,
    ) -> None:
        """Test compute returns NOT_APPLICABLE for patient not in initial population."""
        mock_get_patient.return_value = mock_patient
        mock_in_initial_pop.return_value = False
        mock_create_card.return_value = Mock()

        effects = protocol_instance.compute()

        assert len(effects) == 1
        mock_create_card.assert_called_once()

    @patch.object(CMS138v14TobaccoScreening, "_create_not_applicable_card")
    @patch.object(CMS138v14TobaccoScreening, "_has_hospice_care_in_period")
    @patch.object(CMS138v14TobaccoScreening, "_in_initial_population")
    @patch.object(CMS138v14TobaccoScreening, "_get_patient")
    def test_compute_not_applicable_for_hospice(
        self,
        mock_get_patient: MagicMock,
        mock_in_initial_pop: MagicMock,
        mock_hospice: MagicMock,
        mock_create_card: MagicMock,
        protocol_instance: CMS138v14TobaccoScreening,
        mock_patient: Mock,
    ) -> None:
        """Test compute returns NOT_APPLICABLE for hospice patient."""
        mock_get_patient.return_value = mock_patient
        mock_in_initial_pop.return_value = True
        mock_hospice.return_value = True
        mock_create_card.return_value = Mock()

        effects = protocol_instance.compute()

        assert len(effects) == 1
        mock_create_card.assert_called_once()

    @patch.object(CMS138v14TobaccoScreening, "_create_due_card")
    @patch.object(CMS138v14TobaccoScreening, "_get_screening_data")
    @patch.object(CMS138v14TobaccoScreening, "_has_hospice_care_in_period")
    @patch.object(CMS138v14TobaccoScreening, "_in_initial_population")
    @patch.object(CMS138v14TobaccoScreening, "_get_patient")
    def test_compute_due_for_unscreened_patient(
        self,
        mock_get_patient: MagicMock,
        mock_in_initial_pop: MagicMock,
        mock_hospice: MagicMock,
        mock_get_screening: MagicMock,
        mock_create_card: MagicMock,
        protocol_instance: CMS138v14TobaccoScreening,
        mock_patient: Mock,
    ) -> None:
        """Test compute returns DUE for patient without screening."""
        mock_get_patient.return_value = mock_patient
        mock_in_initial_pop.return_value = True
        mock_hospice.return_value = False
        mock_get_screening.return_value = ScreeningData()
        mock_create_card.return_value = Mock()

        effects = protocol_instance.compute()

        assert len(effects) == 1
        mock_create_card.assert_called_once()

    @patch.object(CMS138v14TobaccoScreening, "_create_satisfied_card")
    @patch.object(CMS138v14TobaccoScreening, "_get_screening_data")
    @patch.object(CMS138v14TobaccoScreening, "_has_hospice_care_in_period")
    @patch.object(CMS138v14TobaccoScreening, "_in_initial_population")
    @patch.object(CMS138v14TobaccoScreening, "_get_patient")
    def test_compute_satisfied_for_non_user(
        self,
        mock_get_patient: MagicMock,
        mock_in_initial_pop: MagicMock,
        mock_hospice: MagicMock,
        mock_get_screening: MagicMock,
        mock_create_card: MagicMock,
        protocol_instance: CMS138v14TobaccoScreening,
        mock_patient: Mock,
    ) -> None:
        """Test compute returns SATISFIED for screened non-user."""
        mock_get_patient.return_value = mock_patient
        mock_in_initial_pop.return_value = True
        mock_hospice.return_value = False

        screening_data = ScreeningData()
        screening_data.most_recent_non_user = arrow.get("2024-06-15")
        mock_get_screening.return_value = screening_data
        mock_create_card.return_value = Mock()

        effects = protocol_instance.compute()

        assert len(effects) == 1
        mock_create_card.assert_called_once()

    @patch.object(CMS138v14TobaccoScreening, "_create_due_card")
    @patch.object(CMS138v14TobaccoScreening, "_get_screening_data")
    @patch.object(CMS138v14TobaccoScreening, "_has_hospice_care_in_period")
    @patch.object(CMS138v14TobaccoScreening, "_in_initial_population")
    @patch.object(CMS138v14TobaccoScreening, "_get_patient")
    def test_compute_due_for_tobacco_user_without_intervention(
        self,
        mock_get_patient: MagicMock,
        mock_in_initial_pop: MagicMock,
        mock_hospice: MagicMock,
        mock_get_screening: MagicMock,
        mock_create_card: MagicMock,
        protocol_instance: CMS138v14TobaccoScreening,
        mock_patient: Mock,
    ) -> None:
        """Test compute returns DUE for tobacco user without intervention."""
        mock_get_patient.return_value = mock_patient
        mock_in_initial_pop.return_value = True
        mock_hospice.return_value = False

        screening_data = ScreeningData()
        screening_data.most_recent_user = arrow.get("2024-06-15")
        mock_get_screening.return_value = screening_data
        mock_create_card.return_value = Mock()

        effects = protocol_instance.compute()

        assert len(effects) == 1
        mock_create_card.assert_called_once()

    @patch.object(CMS138v14TobaccoScreening, "_create_satisfied_card")
    @patch.object(CMS138v14TobaccoScreening, "_get_screening_data")
    @patch.object(CMS138v14TobaccoScreening, "_has_hospice_care_in_period")
    @patch.object(CMS138v14TobaccoScreening, "_in_initial_population")
    @patch.object(CMS138v14TobaccoScreening, "_get_patient")
    def test_compute_satisfied_for_tobacco_user_with_intervention(
        self,
        mock_get_patient: MagicMock,
        mock_in_initial_pop: MagicMock,
        mock_hospice: MagicMock,
        mock_get_screening: MagicMock,
        mock_create_card: MagicMock,
        protocol_instance: CMS138v14TobaccoScreening,
        mock_patient: Mock,
    ) -> None:
        """Test compute returns SATISFIED for tobacco user with intervention."""
        mock_get_patient.return_value = mock_patient
        mock_in_initial_pop.return_value = True
        mock_hospice.return_value = False

        screening_data = ScreeningData()
        screening_data.most_recent_user = arrow.get("2024-06-15")
        screening_data.counseling_date = arrow.get("2024-07-01")
        mock_get_screening.return_value = screening_data
        mock_create_card.return_value = Mock()

        effects = protocol_instance.compute()

        assert len(effects) == 1
        mock_create_card.assert_called_once()
