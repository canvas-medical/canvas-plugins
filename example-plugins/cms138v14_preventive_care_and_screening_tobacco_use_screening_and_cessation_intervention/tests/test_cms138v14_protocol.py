"""Tests for CMS138v14 Tobacco Use Screening and Cessation Intervention Protocol."""

import json
from datetime import date, datetime
from unittest.mock import MagicMock, Mock, patch

import arrow
import pytest
from cms138v14_preventive_care_and_screening_tobacco_use_screening_and_cessation_intervention.protocols.cms138v14_protocol import (
    CMS138v14TobaccoScreening,
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


def test_screening_data_has_screening_true_with_user() -> None:
    """Test has_screening returns True when tobacco user screening exists."""
    data = ScreeningData()
    data.most_recent_user = arrow.get("2024-06-01")
    assert data.has_screening() is True


def test_screening_data_has_screening_true_with_non_user() -> None:
    """Test has_screening returns True when non-user screening exists."""
    data = ScreeningData()
    data.most_recent_non_user = arrow.get("2024-06-01")
    assert data.has_screening() is True


def test_screening_data_is_tobacco_user_false_when_non_user() -> None:
    """Test is_tobacco_user returns False when screening shows non-user."""
    data = ScreeningData()
    data.most_recent_non_user = arrow.get("2024-06-01")
    assert data.is_tobacco_user() is False


def test_screening_data_is_tobacco_user_true_when_user() -> None:
    """Test is_tobacco_user returns True when screening shows user."""
    data = ScreeningData()
    data.most_recent_user = arrow.get("2024-06-01")
    assert data.is_tobacco_user() is True


def test_screening_data_is_tobacco_non_user_true() -> None:
    """Test is_tobacco_non_user returns True when screening shows non-user."""
    data = ScreeningData()
    data.most_recent_non_user = arrow.get("2024-06-01")
    assert data.is_tobacco_non_user() is True


def test_screening_data_is_tobacco_non_user_false_when_user() -> None:
    """Test is_tobacco_non_user returns False when screening shows user."""
    data = ScreeningData()
    data.most_recent_user = arrow.get("2024-06-01")
    assert data.is_tobacco_non_user() is False


def test_screening_data_is_tobacco_user_uses_most_recent() -> None:
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


def test_screening_data_has_intervention_true_with_counseling() -> None:
    """Test has_intervention returns True when counseling exists."""
    data = ScreeningData()
    data.counseling_date = arrow.get("2024-06-01")
    assert data.has_intervention() is True


def test_screening_data_has_intervention_true_with_pharmacotherapy() -> None:
    """Test has_intervention returns True when pharmacotherapy exists."""
    data = ScreeningData()
    data.pharmacotherapy_date = arrow.get("2024-06-01")
    assert data.has_intervention() is True


def test_screening_data_has_intervention_true_with_both() -> None:
    """Test has_intervention returns True when both interventions exist."""
    data = ScreeningData()
    data.counseling_date = arrow.get("2024-05-01")
    data.pharmacotherapy_date = arrow.get("2024-06-01")
    assert data.has_intervention() is True


@patch("canvas_sdk.v1.data.Patient.objects")
def test_get_patient_from_patient_event(
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
    mock_condition_objects: MagicMock,
    mock_event_condition_created: Mock,
    mock_patient: Mock,
) -> None:
    """Test getting patient from CONDITION_CREATED event."""
    mock_condition = Mock()
    mock_condition.patient = mock_patient
    mock_condition_objects.filter.return_value.select_related.return_value.first.return_value = (
        mock_condition
    )

    protocol = CMS138v14TobaccoScreening(mock_event_condition_created)
    patient = protocol._get_patient()

    assert patient == mock_patient


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_get_patient_returns_none_when_condition_not_found(
    mock_condition_objects: MagicMock,
    mock_event_condition_created: Mock,
) -> None:
    """Test returns None when condition not found."""
    mock_condition_objects.filter.return_value.select_related.return_value.first.return_value = None

    protocol = CMS138v14TobaccoScreening(mock_event_condition_created)
    patient = protocol._get_patient()

    assert patient is None


def test_chart_context_true_for_patient_updated() -> None:
    """Test _is_chart_context returns True for PATIENT_UPDATED event."""
    event = Mock()
    event.type = EventType.PATIENT_UPDATED
    event.target = Mock()
    event.target.id = "patient-123"
    event.context = {}

    protocol = CMS138v14TobaccoScreening(event)
    assert protocol._is_chart_context() is True


def test_chart_context_true_when_patient_in_context(mock_event_interview_created: Mock) -> None:
    """Test _is_chart_context returns True when patient in event context."""
    protocol = CMS138v14TobaccoScreening(mock_event_interview_created)
    assert protocol._is_chart_context() is True


def test_chart_context_false_when_no_patient_context() -> None:
    """Test _is_chart_context returns False when no patient in context."""
    event = Mock()
    event.type = EventType.CLAIM_CREATED
    event.target = Mock()
    event.target.id = "claim-123"
    event.context = {}

    protocol = CMS138v14TobaccoScreening(event)
    assert protocol._is_chart_context() is False


def test_not_in_population_no_birth_date(protocol_instance: CMS138v14TobaccoScreening) -> None:
    """Test patient without birth date is not in initial population."""
    patient = Mock(spec=Patient)
    patient.first_name = "Test"
    patient.birth_date = None

    in_pop = protocol_instance._in_initial_population(patient)

    assert in_pop is False


def test_not_in_population_age_under_12(
    protocol_instance: CMS138v14TobaccoScreening,
    mock_patient_child: Mock,
) -> None:
    """Test patient under 12 is not in initial population."""
    in_pop = protocol_instance._in_initial_population(mock_patient_child)

    assert in_pop is False


def test_in_population_age_12_plus_chart_context(
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


@patch("canvas_sdk.v1.data.claim_line_item.ClaimLineItem.objects")
@patch("canvas_sdk.v1.data.encounter.Encounter.objects")
def test_count_qualifying_visits_from_encounters(
    mock_encounter_objects: MagicMock,
    mock_claim_objects: MagicMock,
    protocol_instance: CMS138v14TobaccoScreening,
    mock_patient: Mock,
) -> None:
    """Test counting qualifying visits from Encounter model."""
    mock_encounter_objects.filter.return_value.values_list.return_value = [
        "note-1",
        "note-2",
        "note-3",
    ]
    mock_claim_objects.filter.return_value.values_list.return_value = []

    count = protocol_instance._count_qualifying_visits(mock_patient)

    assert count == 3


@patch("canvas_sdk.v1.data.claim_line_item.ClaimLineItem.objects")
@patch("canvas_sdk.v1.data.encounter.Encounter.objects")
def test_count_qualifying_visits_from_claims(
    mock_encounter_objects: MagicMock,
    mock_claim_objects: MagicMock,
    protocol_instance: CMS138v14TobaccoScreening,
    mock_patient: Mock,
) -> None:
    """Test counting qualifying visits from ClaimLineItem model."""
    mock_encounter_objects.filter.return_value.values_list.return_value = []
    mock_claim_objects.filter.return_value.values_list.return_value = ["note-1", "note-2"]

    count = protocol_instance._count_qualifying_visits(mock_patient)

    assert count == 2


@patch("canvas_sdk.v1.data.claim_line_item.ClaimLineItem.objects")
@patch("canvas_sdk.v1.data.encounter.Encounter.objects")
def test_count_qualifying_visits_deduplicates_same_note(
    mock_encounter_objects: MagicMock,
    mock_claim_objects: MagicMock,
    protocol_instance: CMS138v14TobaccoScreening,
    mock_patient: Mock,
) -> None:
    """Test that visits from same note are not double-counted."""
    mock_encounter_objects.filter.return_value.values_list.return_value = ["note-1"]
    mock_claim_objects.filter.return_value.values_list.return_value = ["note-1"]

    count = protocol_instance._count_qualifying_visits(mock_patient)

    assert count == 1


@patch("canvas_sdk.v1.data.claim_line_item.ClaimLineItem.objects")
@patch("canvas_sdk.v1.data.encounter.Encounter.objects")
def test_count_preventive_visits_from_encounters(
    mock_encounter_objects: MagicMock,
    mock_claim_objects: MagicMock,
    protocol_instance: CMS138v14TobaccoScreening,
    mock_patient: Mock,
) -> None:
    """Test counting preventive visits from Encounter model."""
    mock_encounter_objects.filter.return_value.values_list.return_value = ["note-1"]
    mock_claim_objects.filter.return_value.values_list.return_value = []

    count = protocol_instance._count_preventive_visits(mock_patient)

    assert count == 1


@patch("canvas_sdk.v1.data.claim_line_item.ClaimLineItem.objects")
@patch("canvas_sdk.v1.data.encounter.Encounter.objects")
def test_count_preventive_visits_deduplicates_same_note(
    mock_encounter_objects: MagicMock,
    mock_claim_objects: MagicMock,
    protocol_instance: CMS138v14TobaccoScreening,
    mock_patient: Mock,
) -> None:
    """Test that preventive visits from same note are not double-counted."""
    mock_encounter_objects.filter.return_value.values_list.return_value = ["note-1"]
    mock_claim_objects.filter.return_value.values_list.return_value = ["note-1"]

    count = protocol_instance._count_preventive_visits(mock_patient)

    assert count == 1


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_hospice_diagnosis(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS138v14TobaccoScreening,
    mock_patient: Mock,
) -> None:
    """Test returns True when hospice diagnosis exists."""
    mock_condition_objects.for_patient.return_value.find.return_value.committed.return_value.filter.return_value.exists.return_value = True

    result = protocol_instance._has_hospice_care_in_period(mock_patient)

    assert result is True


@patch("canvas_sdk.v1.data.instruction.Instruction.objects")
@patch("canvas_sdk.v1.data.claim_line_item.ClaimLineItem.objects")
@patch("canvas_sdk.v1.data.Observation.objects")
@patch("canvas_sdk.v1.data.encounter.Encounter.objects")
@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_no_hospice_care(
    mock_condition_objects: MagicMock,
    mock_encounter_objects: MagicMock,
    mock_observation_objects: MagicMock,
    mock_claim_objects: MagicMock,
    mock_instruction_objects: MagicMock,
    protocol_instance: CMS138v14TobaccoScreening,
    mock_patient: Mock,
) -> None:
    """Test returns False when no hospice care indicators."""
    mock_condition_objects.for_patient.return_value.find.return_value.committed.return_value.filter.return_value.exists.return_value = False
    mock_encounter_objects.filter.return_value.exists.return_value = False
    mock_encounter_objects.filter.return_value.values_list.return_value = []
    mock_observation_objects.for_patient.return_value.committed.return_value.filter.return_value.exists.return_value = False
    mock_claim_objects.filter.return_value.exists.return_value = False
    mock_instruction_objects.for_patient.return_value.committed.return_value.find.return_value.filter.return_value.exists.return_value = False

    result = protocol_instance._has_hospice_care_in_period(mock_patient)

    assert result is False


@patch("canvas_sdk.v1.data.questionnaire.InterviewQuestionResponse.objects")
def test_check_interview_responses_finds_tobacco_user(
    mock_interview_objects: MagicMock,
    protocol_instance: CMS138v14TobaccoScreening,
    mock_patient: Mock,
) -> None:
    """Test finds tobacco user response from interview."""
    mock_interview = Mock()
    mock_interview.created = datetime(2024, 6, 15, 10, 0, 0)

    mock_response_option = Mock()
    mock_response_option.code = "449868002"

    mock_response = Mock()
    mock_response.interview = mock_interview
    mock_response.response_option = mock_response_option

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
def test_check_interview_responses_finds_tobacco_non_user(
    mock_interview_objects: MagicMock,
    protocol_instance: CMS138v14TobaccoScreening,
    mock_patient: Mock,
) -> None:
    """Test finds tobacco non-user response from interview."""
    mock_interview = Mock()
    mock_interview.created = datetime(2024, 6, 15, 10, 0, 0)

    mock_response_option = Mock()
    mock_response_option.code = "266919005"

    mock_response = Mock()
    mock_response.interview = mock_interview
    mock_response.response_option = mock_response_option

    mock_interview_objects.filter.return_value.select_related.return_value.order_by.return_value.first.return_value = mock_response

    result = ScreeningData()
    tobacco_user_codes = {"449868002"}
    tobacco_non_user_codes = {"266919005"}

    protocol_instance._check_interview_responses(
        mock_patient, result, tobacco_user_codes, tobacco_non_user_codes
    )

    assert result.most_recent_non_user is not None
    assert result.is_tobacco_non_user() is True


def test_compute_populations_population_1_no_screening(
    protocol_instance: CMS138v14TobaccoScreening,
) -> None:
    """Test Population 1 numerator is False when no screening."""
    data = ScreeningData()

    protocol_instance._compute_populations(data)

    pop1 = protocol_instance._populations[CMS138v14TobaccoScreening.POPULATION_1]
    assert pop1.in_numerator is False


def test_compute_populations_population_1_has_screening(
    protocol_instance: CMS138v14TobaccoScreening,
) -> None:
    """Test Population 1 numerator is True when screened."""
    data = ScreeningData()
    data.most_recent_non_user = arrow.get("2024-06-01")

    protocol_instance._compute_populations(data)

    pop1 = protocol_instance._populations[CMS138v14TobaccoScreening.POPULATION_1]
    assert pop1.in_numerator is True


def test_compute_populations_population_2_not_tobacco_user(
    protocol_instance: CMS138v14TobaccoScreening,
) -> None:
    """Test Population 2 denominator is False when not tobacco user."""
    data = ScreeningData()
    data.most_recent_non_user = arrow.get("2024-06-01")

    protocol_instance._compute_populations(data)

    pop2 = protocol_instance._populations[CMS138v14TobaccoScreening.POPULATION_2]
    assert pop2.in_denominator is False
    assert pop2.in_numerator is False


def test_compute_populations_population_2_tobacco_user_no_intervention(
    protocol_instance: CMS138v14TobaccoScreening,
) -> None:
    """Test Population 2 numerator is False when tobacco user without intervention."""
    data = ScreeningData()
    data.most_recent_user = arrow.get("2024-06-01")

    protocol_instance._compute_populations(data)

    pop2 = protocol_instance._populations[CMS138v14TobaccoScreening.POPULATION_2]
    assert pop2.in_denominator is True
    assert pop2.in_numerator is False


def test_compute_populations_population_2_tobacco_user_with_intervention(
    protocol_instance: CMS138v14TobaccoScreening,
) -> None:
    """Test Population 2 numerator is True when tobacco user has intervention."""
    data = ScreeningData()
    data.most_recent_user = arrow.get("2024-06-01")
    data.counseling_date = arrow.get("2024-07-01")

    protocol_instance._compute_populations(data)

    pop2 = protocol_instance._populations[CMS138v14TobaccoScreening.POPULATION_2]
    assert pop2.in_numerator is True


def test_compute_populations_population_3_non_user_screened(
    protocol_instance: CMS138v14TobaccoScreening,
) -> None:
    """Test Population 3 numerator is True for screened non-user."""
    data = ScreeningData()
    data.most_recent_non_user = arrow.get("2024-06-01")

    protocol_instance._compute_populations(data)

    pop3 = protocol_instance._populations[CMS138v14TobaccoScreening.POPULATION_3]
    assert pop3.in_numerator is True


def test_compute_populations_population_3_user_without_intervention(
    protocol_instance: CMS138v14TobaccoScreening,
) -> None:
    """Test Population 3 numerator is False for tobacco user without intervention."""
    data = ScreeningData()
    data.most_recent_user = arrow.get("2024-06-01")

    protocol_instance._compute_populations(data)

    pop3 = protocol_instance._populations[CMS138v14TobaccoScreening.POPULATION_3]
    assert pop3.in_numerator is False


def test_compute_populations_population_3_user_with_intervention(
    protocol_instance: CMS138v14TobaccoScreening,
) -> None:
    """Test Population 3 numerator is True for tobacco user with intervention."""
    data = ScreeningData()
    data.most_recent_user = arrow.get("2024-06-01")
    data.pharmacotherapy_date = arrow.get("2024-07-01")

    protocol_instance._compute_populations(data)

    pop3 = protocol_instance._populations[CMS138v14TobaccoScreening.POPULATION_3]
    assert pop3.in_numerator is True


def test_get_value_set_codes_single_attribute(
    protocol_instance: CMS138v14TobaccoScreening,
) -> None:
    """Test getting codes from single attribute."""

    class MockValueSet:
        SNOMEDCT = {"code1", "code2"}

    codes = protocol_instance._get_value_set_codes(MockValueSet, "SNOMEDCT")

    assert codes == {"code1", "code2"}


def test_get_value_set_codes_multiple_attributes(
    protocol_instance: CMS138v14TobaccoScreening,
) -> None:
    """Test getting codes from multiple attributes."""

    class MockValueSet:
        SNOMEDCT = {"snomed1"}
        CPT = {"cpt1", "cpt2"}

    codes = protocol_instance._get_value_set_codes(MockValueSet, "SNOMEDCT", "CPT")

    assert codes == {"snomed1", "cpt1", "cpt2"}


def test_get_value_set_codes_missing_attribute(
    protocol_instance: CMS138v14TobaccoScreening,
) -> None:
    """Test returns empty set for missing attribute."""

    class MockValueSet:
        SNOMEDCT = {"code1"}

    codes = protocol_instance._get_value_set_codes(MockValueSet, "ICD10CM")

    assert codes == set()


def test_create_not_applicable_card_has_correct_status(
    protocol_instance: CMS138v14TobaccoScreening, mock_patient: Mock
) -> None:
    """Test NOT_APPLICABLE card has correct status and empty narrative."""
    effect = protocol_instance._create_not_applicable_card(mock_patient)

    assert effect is not None
    payload = json.loads(effect.payload)
    assert payload["data"]["status"] == "not_applicable"
    assert payload["data"]["narrative"] == ""
    assert payload["patient"] == mock_patient.id


def test_create_satisfied_card_non_user_includes_screening_date(
    protocol_instance: CMS138v14TobaccoScreening, mock_patient: Mock
) -> None:
    """Test SATISFIED card for non-user includes screening date in narrative."""
    data = ScreeningData()
    data.most_recent_non_user = arrow.get("2024-06-15")

    effect = protocol_instance._create_satisfied_card(mock_patient, data)

    payload = json.loads(effect.payload)
    assert payload["data"]["status"] == "satisfied"
    assert "6/15/24" in payload["data"]["narrative"]
    assert "non-tobacco user" in payload["data"]["narrative"]


def test_create_satisfied_card_user_with_counseling_includes_intervention_date(
    protocol_instance: CMS138v14TobaccoScreening, mock_patient: Mock
) -> None:
    """Test SATISFIED card for user with intervention includes counseling date."""
    data = ScreeningData()
    data.most_recent_user = arrow.get("2024-06-15")
    data.counseling_date = arrow.get("2024-07-01")

    effect = protocol_instance._create_satisfied_card(mock_patient, data)

    payload = json.loads(effect.payload)
    assert payload["data"]["status"] == "satisfied"
    assert "tobacco user" in payload["data"]["narrative"]
    assert "7/1/24" in payload["data"]["narrative"]
    assert "counseling" in payload["data"]["narrative"]


def test_create_satisfied_card_user_with_pharmacotherapy_includes_medication_date(
    protocol_instance: CMS138v14TobaccoScreening, mock_patient: Mock
) -> None:
    """Test SATISFIED card for user with pharmacotherapy includes medication date."""
    data = ScreeningData()
    data.most_recent_user = arrow.get("2024-06-15")
    data.pharmacotherapy_date = arrow.get("2024-08-01")

    effect = protocol_instance._create_satisfied_card(mock_patient, data)

    payload = json.loads(effect.payload)
    assert payload["data"]["status"] == "satisfied"
    assert "8/1/24" in payload["data"]["narrative"]
    assert "pharmacotherapy" in payload["data"]["narrative"]


def test_create_due_card_for_unscreened_patient_has_screening_recommendation(
    protocol_instance: CMS138v14TobaccoScreening, mock_patient: Mock
) -> None:
    """Test DUE card for unscreened patient includes screening recommendation."""
    data = ScreeningData()

    effect = protocol_instance._create_due_card(mock_patient, data)

    payload = json.loads(effect.payload)
    assert payload["data"]["status"] == "due"
    assert "screened" in payload["data"]["narrative"]
    recommendations = payload["data"].get("recommendations", [])
    assert len(recommendations) >= 1


def test_create_due_card_for_tobacco_user_has_intervention_recommendations(
    protocol_instance: CMS138v14TobaccoScreening, mock_patient: Mock
) -> None:
    """Test DUE card for tobacco user includes counseling and medication recommendations."""
    data = ScreeningData()
    data.most_recent_user = arrow.get("2024-06-15")

    effect = protocol_instance._create_due_card(mock_patient, data)

    payload = json.loads(effect.payload)
    assert payload["data"]["status"] == "due"
    assert "tobacco user" in payload["data"]["narrative"]
    assert "intervention" in payload["data"]["narrative"]
    recommendations = payload["data"].get("recommendations", [])
    # Should have counseling and pharmacotherapy recommendations
    assert len(recommendations) >= 2


@patch.object(CMS138v14TobaccoScreening, "_get_patient")
def test_compute_returns_empty_when_no_patient(
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
