import arrow
import pytest
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch
from collections.abc import Generator
from typing import Any

from canvas_sdk.effects.protocol_card import ProtocolCard
from canvas_sdk.events import EventType
from canvas_sdk.v1.data import Patient
from canvas_sdk.v1.data.condition import Condition
from canvas_sdk.v1.data.questionnaire import Interview, InterviewQuestionResponse
from canvas_sdk.v1.data.medication import Medication
from canvas_sdk.v1.data.claim_line_item import ClaimLineItem

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from protocols.cms131v14_protocol import CMS131v14DiabetesEyeExam


@pytest.fixture
def mock_patient() -> Mock:
    """Create a mock patient."""
    patient = Mock(spec=Patient)
    patient.id = "patient-123"
    patient.first_name = "John"
    patient.last_name = "Doe"
    patient.birth_date = "1970-01-01"

    def age_at(date):
        birth = arrow.get("1970-01-01")
        target = date if isinstance(date, arrow.Arrow) else arrow.get(date)
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
    condition.entered_in_error = False

    # Mock codings
    coding_mock = Mock()
    coding_mock.code = "E11.9"
    coding_mock.system = "ICD10"
    condition.codings = Mock()
    condition.codings.all = Mock(return_value=[coding_mock])

    return condition


@pytest.fixture
def mock_event() -> Mock:
    """Create a mock event."""
    event = Mock()
    event.type = EventType.CONDITION_CREATED
    event.target = Mock()
    event.target.id = "condition-123"
    return event


@pytest.fixture
def mock_timeframe() -> Mock:
    """Create a mock timeframe for measurement period."""
    timeframe = Mock()
    timeframe.start = arrow.get("2024-01-01")
    timeframe.end = arrow.get("2024-12-31")
    return timeframe


@pytest.fixture
def protocol_instance(mock_event, mock_timeframe) -> CMS131v14DiabetesEyeExam:
    """Create a protocol instance with mocked dependencies."""
    protocol = CMS131v14DiabetesEyeExam(mock_event)
    return protocol


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_get_patient_with_condition_created_event(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
    mock_condition: Mock,
):
    """Test _get_patient returns patient and condition for CONDITION_CREATED event."""
    mock_condition.patient = mock_patient
    mock_condition_objects.filter.return_value.select_related.return_value.first.return_value = (
        mock_condition
    )

    patient, condition = protocol_instance._get_patient()
    assert patient == mock_patient
    assert condition == mock_condition
    mock_condition_objects.filter.assert_called_once_with(id="condition-123")


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_get_patient_when_condition_not_found(
    mock_condition_objects: MagicMock, protocol_instance: CMS131v14DiabetesEyeExam
):
    """Test _get_patient returns None when condition not found."""
    mock_condition_objects.filter.return_value.select_related.return_value.first.return_value = (
        None
    )

    patient, condition = protocol_instance._get_patient()

    assert patient is None
    assert condition is None


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_is_condition_diabetes_returns_true(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_condition: Mock,
):
    """Test _is_condition_diabetes returns True for diabetes condition."""
    mock_condition_objects.filter.return_value.find.return_value.exists.return_value = (
        True
    )
    result = protocol_instance._is_condition_diabetes(mock_condition)
    assert result is True
    mock_condition_objects.filter.assert_called_once_with(id=mock_condition.id)


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_is_condition_diabetes_returns_false(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_condition: Mock,
):
    """Test _is_condition_diabetes returns False for non-diabetes condition."""
    mock_condition_objects.filter.return_value.find.return_value.exists.return_value = (
        False
    )
    result = protocol_instance._is_condition_diabetes(mock_condition)
    assert result is False


def test_should_remove_card_with_no_condition(
    protocol_instance: CMS131v14DiabetesEyeExam, mock_patient: Mock
):
    """Test _should_remove_card returns False when condition is None."""
    result = protocol_instance._should_remove_card(mock_patient, None)
    assert result is False


@patch.object(CMS131v14DiabetesEyeExam, "_is_condition_diabetes")
def test_should_remove_card_with_non_diabetes_condition(
    mock_is_diabetes: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
    mock_condition: Mock,
):
    """Test _should_remove_card returns False for non-diabetes condition."""
    mock_is_diabetes.return_value = False

    result = protocol_instance._should_remove_card(mock_patient, mock_condition)
    assert result is False
    mock_is_diabetes.assert_called_once_with(mock_condition)


@patch.object(CMS131v14DiabetesEyeExam, "_has_diabetes_diagnosis")
@patch.object(CMS131v14DiabetesEyeExam, "_is_condition_diabetes")
def test_should_remove_card_diabetes_entered_in_error_no_other_diabetes(
    mock_is_diabetes: MagicMock,
    mock_has_diabetes: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
    mock_condition: Mock,
):
    """Test _should_remove_card returns True when diabetes entered in error and no other diabetes."""
    mock_condition.entered_in_error = True
    mock_is_diabetes.return_value = True
    mock_has_diabetes.return_value = False

    result = protocol_instance._should_remove_card(mock_patient, mock_condition)
    assert result is True
    mock_has_diabetes.assert_called_once_with(mock_patient)


def test_in_initial_population_age_too_young(
    protocol_instance: CMS131v14DiabetesEyeExam, mock_patient: Mock
):
    """Test _in_initial_population returns False for age < 18."""
    result = protocol_instance._in_initial_population(mock_patient, age=17)
    assert result is False


def test_in_initial_population_age_too_old(
    protocol_instance: CMS131v14DiabetesEyeExam, mock_patient: Mock
):
    """Test _in_initial_population returns False for age > 75."""
    result = protocol_instance._in_initial_population(mock_patient, age=76)
    assert result is False


@patch.object(CMS131v14DiabetesEyeExam, "_has_eligible_encounter_in_period")
@patch.object(CMS131v14DiabetesEyeExam, "_has_diabetes_diagnosis_overlapping_period")
def test_in_initial_population_no_diabetes(
    mock_has_diabetes: MagicMock,
    mock_has_encounter: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
):
    """Test _in_initial_population returns False when no diabetes."""
    mock_has_diabetes.return_value = False

    result = protocol_instance._in_initial_population(mock_patient, age=50)
    assert result is False
    mock_has_diabetes.assert_called_once_with(mock_patient)
    mock_has_encounter.assert_not_called()


@patch.object(CMS131v14DiabetesEyeExam, "_has_eligible_encounter_in_period")
@patch.object(CMS131v14DiabetesEyeExam, "_has_diabetes_diagnosis_overlapping_period")
def test_in_initial_population_all_criteria_met(
    mock_has_diabetes: MagicMock,
    mock_has_encounter: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
):
    """Test _in_initial_population returns True when all criteria met."""
    mock_has_diabetes.return_value = True
    mock_has_encounter.return_value = True

    result = protocol_instance._in_initial_population(mock_patient, age=50)
    assert result is True


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_diabetes_diagnosis_true(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
):
    """Test _has_diabetes_diagnosis returns True when diabetes exists."""
    mock_condition_objects.for_patient.return_value.find.return_value.active.return_value.exists.return_value = (
        True
    )

    result = protocol_instance._has_diabetes_diagnosis(mock_patient)
    assert result is True
    mock_condition_objects.for_patient.assert_called_once_with(mock_patient.id)


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_diabetes_diagnosis_false(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
):
    """Test _has_diabetes_diagnosis returns False when no diabetes."""
    mock_condition_objects.for_patient.return_value.find.return_value.active.return_value.exists.return_value = (
        False
    )

    result = protocol_instance._has_diabetes_diagnosis(mock_patient)
    assert result is False


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_diabetes_diagnosis_overlapping_period_true(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
):
    """Test _has_diabetes_diagnosis_overlapping_period returns True."""
    mock_condition_objects.for_patient.return_value.find.return_value.active.return_value.exists.return_value = (
        True
    )

    result = protocol_instance._has_diabetes_diagnosis_overlapping_period(mock_patient)
    assert result is True


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_diabetes_diagnosis_overlapping_period_false(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
):
    """Test _has_diabetes_diagnosis_overlapping_period returns False."""
    mock_condition_objects.for_patient.return_value.find.return_value.active.return_value.exists.return_value = (
        False
    )

    result = protocol_instance._has_diabetes_diagnosis_overlapping_period(mock_patient)
    assert result is False


@patch("canvas_sdk.v1.data.questionnaire.InterviewQuestionResponse.objects")
@patch("canvas_sdk.v1.data.questionnaire.Interview.objects")
def test_has_hospice_care_in_period_true(
    mock_interview_objects: MagicMock,
    mock_response_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
):
    """Test _has_hospice_care_in_period returns True when hospice response found."""
    # Mock interviews exist
    mock_interview_objects.filter.return_value.exists.return_value = True
    mock_interview_objects.filter.return_value.values_list.return_value = [
        "interview-123"
    ]

    # Mock response with hospice code
    mock_response_option = Mock()
    mock_response_option.code = "428361000124107"  # Hospice code
    mock_response = Mock()
    mock_response.response_option = mock_response_option
    mock_response_objects.filter.return_value.select_related.return_value = [
        mock_response
    ]

    result = protocol_instance._has_hospice_care_in_period(mock_patient)
    assert result is True


@patch("canvas_sdk.v1.data.questionnaire.Interview.objects")
def test_has_hospice_care_in_period_false_no_interviews(
    mock_interview_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
):
    """Test _has_hospice_care_in_period returns False when no interviews."""
    mock_interview_objects.filter.return_value.exists.return_value = False

    result = protocol_instance._has_hospice_care_in_period(mock_patient)
    assert result is False


def test_is_age_66_plus_with_frailty_age_less_than_66(
    protocol_instance: CMS131v14DiabetesEyeExam, mock_patient: Mock
):
    """Test _is_age_66_plus_with_frailty returns False for age < 66."""
    result = protocol_instance._is_age_66_plus_with_frailty(mock_patient, age=65)
    assert result is False


@patch("canvas_sdk.v1.data.questionnaire.InterviewQuestionResponse.objects")
@patch("canvas_sdk.v1.data.questionnaire.Interview.objects")
def test_is_age_66_plus_with_frailty_true(
    mock_interview_objects: MagicMock,
    mock_response_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
):
    """Test _is_age_66_plus_with_frailty returns True when age 66+ with frailty."""
    # Mock interviews exist
    mock_interview_objects.filter.return_value.exists.return_value = True
    mock_interview_objects.filter.return_value.values_list.return_value = [
        "interview-123"
    ]

    # Mock response with frailty code
    mock_response_option = Mock()
    mock_response_option.code = "105501005"  # Frailty Device code
    mock_response = Mock()
    mock_response.response_option = mock_response_option
    mock_response_objects.filter.return_value.select_related.return_value = [
        mock_response
    ]

    result = protocol_instance._is_age_66_plus_with_frailty(mock_patient, age=70)
    assert result is True


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_advanced_illness_or_dementia_meds_has_advanced_illness(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
):
    """Test _has_advanced_illness_or_dementia_meds returns True for advanced illness."""
    mock_condition_objects.for_patient.return_value.active.return_value.find.return_value.exists.return_value = (
        True
    )

    result = protocol_instance._has_advanced_illness_or_dementia_meds(mock_patient)
    assert result is True


@patch("canvas_sdk.v1.data.medication.Medication.objects")
@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_advanced_illness_or_dementia_meds_has_dementia_meds(
    mock_condition_objects: MagicMock,
    mock_medication_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
):
    """Test _has_advanced_illness_or_dementia_meds returns True for dementia meds."""
    # No advanced illness
    mock_condition_objects.for_patient.return_value.active.return_value.find.return_value.exists.return_value = (
        False
    )

    # Has dementia meds
    mock_medication_objects.for_patient.return_value.active.return_value.find.return_value.filter.return_value.exists.return_value = (
        True
    )

    result = protocol_instance._has_advanced_illness_or_dementia_meds(mock_patient)
    assert result is True


@patch("canvas_sdk.v1.data.medication.Medication.objects")
@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_advanced_illness_or_dementia_meds_false(
    mock_condition_objects: MagicMock,
    mock_medication_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
):
    """Test _has_advanced_illness_or_dementia_meds returns False when neither exists."""
    mock_condition_objects.for_patient.return_value.active.return_value.find.return_value.exists.return_value = (
        False
    )
    mock_medication_objects.for_patient.return_value.active.return_value.find.return_value.filter.return_value.exists.return_value = (
        False
    )

    result = protocol_instance._has_advanced_illness_or_dementia_meds(mock_patient)
    assert result is False


def test_is_age_66_plus_in_nursing_home_age_less_than_66(
    protocol_instance: CMS131v14DiabetesEyeExam, mock_patient: Mock
):
    """Test _is_age_66_plus_in_nursing_home returns False for age < 66."""
    result = protocol_instance._is_age_66_plus_in_nursing_home(mock_patient, age=65)
    assert result is False


@patch("canvas_sdk.v1.data.claim_line_item.ClaimLineItem.objects")
def test_is_age_66_plus_in_nursing_home_true(
    mock_claim_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
):
    """Test _is_age_66_plus_in_nursing_home returns True when nursing home claim found."""
    mock_claim = Mock()
    mock_claim.proc_code = "99304"
    mock_claim_objects.filter.return_value.exists.return_value = True
    mock_claim_objects.filter.return_value.first.return_value = mock_claim

    result = protocol_instance._is_age_66_plus_in_nursing_home(mock_patient, age=70)
    assert result is True


@patch("canvas_sdk.v1.data.claim_line_item.ClaimLineItem.objects")
def test_is_age_66_plus_in_nursing_home_false(
    mock_claim_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
):
    """Test _is_age_66_plus_in_nursing_home returns False when no nursing home claim."""
    mock_claim_objects.filter.return_value.exists.return_value = False

    result = protocol_instance._is_age_66_plus_in_nursing_home(mock_patient, age=70)
    assert result is False


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_palliative_care_in_period_has_condition(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
):
    """Test _has_palliative_care_in_period returns True for palliative condition."""
    mock_condition_objects.for_patient.return_value.active.return_value.find.return_value.exists.return_value = (
        True
    )

    result = protocol_instance._has_palliative_care_in_period(mock_patient)
    assert result is True


@patch("canvas_sdk.v1.data.claim_line_item.ClaimLineItem.objects")
@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_palliative_care_in_period_has_claim(
    mock_condition_objects: MagicMock,
    mock_claim_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
):
    """Test _has_palliative_care_in_period returns True for palliative claim."""
    # No palliative condition
    mock_condition_objects.for_patient.return_value.active.return_value.find.return_value.exists.return_value = (
        False
    )

    # Has palliative claim
    mock_claim = Mock()
    mock_claim.proc_code = "M1141"
    mock_claim_objects.filter.return_value.exists.return_value = True
    mock_claim_objects.filter.return_value.first.return_value = mock_claim

    result = protocol_instance._has_palliative_care_in_period(mock_patient)
    assert result is True


@patch("canvas_sdk.v1.data.claim_line_item.ClaimLineItem.objects")
@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_palliative_care_in_period_false(
    mock_condition_objects: MagicMock,
    mock_claim_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
):
    """Test _has_palliative_care_in_period returns False when neither exists."""
    mock_condition_objects.for_patient.return_value.active.return_value.find.return_value.exists.return_value = (
        False
    )
    mock_claim_objects.filter.return_value.exists.return_value = False

    result = protocol_instance._has_palliative_care_in_period(mock_patient)
    assert result is False


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_bilateral_absence_of_eyes_true(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
):
    """Test _has_bilateral_absence_of_eyes returns True when condition exists."""
    mock_condition_objects.for_patient.return_value.active.return_value.filter.return_value.exists.return_value = (
        True
    )

    result = protocol_instance._has_bilateral_absence_of_eyes(mock_patient)
    assert result is True


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_bilateral_absence_of_eyes_false(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
):
    """Test _has_bilateral_absence_of_eyes returns False when condition doesn't exist."""
    mock_condition_objects.for_patient.return_value.active.return_value.filter.return_value.exists.return_value = (
        False
    )

    result = protocol_instance._has_bilateral_absence_of_eyes(mock_patient)
    assert result is False


@patch.object(CMS131v14DiabetesEyeExam, "_has_hospice_care_in_period")
def test_in_denominator_excluded_by_hospice(
    mock_has_hospice: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
):
    """Test _in_denominator returns False when patient in hospice."""
    mock_has_hospice.return_value = True

    result = protocol_instance._in_denominator(mock_patient, age=70)
    assert result is False


@patch.object(CMS131v14DiabetesEyeExam, "_has_advanced_illness_or_dementia_meds")
@patch.object(CMS131v14DiabetesEyeExam, "_is_age_66_plus_with_frailty")
@patch.object(CMS131v14DiabetesEyeExam, "_has_hospice_care_in_period")
def test_in_denominator_excluded_by_frailty_and_advanced_illness(
    mock_has_hospice: MagicMock,
    mock_is_frailty: MagicMock,
    mock_has_advanced_illness: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
):
    """Test _in_denominator returns False when age 66+ with frailty and advanced illness."""
    mock_has_hospice.return_value = False
    mock_is_frailty.return_value = True
    mock_has_advanced_illness.return_value = True

    result = protocol_instance._in_denominator(mock_patient, age=70)
    assert result is False


@patch.object(CMS131v14DiabetesEyeExam, "_has_bilateral_absence_of_eyes")
@patch.object(CMS131v14DiabetesEyeExam, "_has_palliative_care_in_period")
@patch.object(CMS131v14DiabetesEyeExam, "_is_age_66_plus_in_nursing_home")
@patch.object(CMS131v14DiabetesEyeExam, "_has_advanced_illness_or_dementia_meds")
@patch.object(CMS131v14DiabetesEyeExam, "_is_age_66_plus_with_frailty")
@patch.object(CMS131v14DiabetesEyeExam, "_has_hospice_care_in_period")
def test_in_denominator_no_exclusions(
    mock_has_hospice: MagicMock,
    mock_is_frailty: MagicMock,
    mock_has_advanced_illness: MagicMock,
    mock_is_nursing_home: MagicMock,
    mock_has_palliative: MagicMock,
    mock_has_bilateral: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
):
    """Test _in_denominator returns True when no exclusions apply."""
    mock_has_hospice.return_value = False
    mock_is_frailty.return_value = False
    mock_has_advanced_illness.return_value = False
    mock_is_nursing_home.return_value = False
    mock_has_palliative.return_value = False
    mock_has_bilateral.return_value = False

    result = protocol_instance._in_denominator(mock_patient, age=50)
    assert result is True


@patch.object(CMS131v14DiabetesEyeExam, "_has_retinal_finding_no_severity_in_prior_year")
@patch.object(CMS131v14DiabetesEyeExam, "_has_retinal_finding_with_severity_in_period")
@patch.object(CMS131v14DiabetesEyeExam, "_has_autonomous_eye_exam_in_period")
@patch.object(CMS131v14DiabetesEyeExam, "_has_retinal_exam_in_period_or_year_prior")
@patch.object(CMS131v14DiabetesEyeExam, "_has_retinal_exam_in_period")
@patch.object(CMS131v14DiabetesEyeExam, "_has_retinopathy_diagnosis_in_period")
def test_in_numerator_true_with_retinopathy_exam(
    mock_has_retinopathy: MagicMock,
    mock_exam_in_period_or_year_prior: MagicMock,
    mock_exam_in_lookback: MagicMock,
    mock_autonomous_exam: MagicMock,
    mock_severity_finding: MagicMock,
    mock_no_severity_prior: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
):
    """Retinopathy diagnosis plus eye-care exam during measurement period qualifies numerator."""
    mock_has_retinopathy.return_value = True
    mock_exam_in_period_or_year_prior.return_value = True
    mock_exam_in_lookback.return_value = False
    mock_autonomous_exam.return_value = False
    mock_severity_finding.return_value = False
    mock_no_severity_prior.return_value = False

    assert protocol_instance._in_numerator(mock_patient) is True
    mock_exam_in_period_or_year_prior.assert_called_once_with(mock_patient)


@patch.object(CMS131v14DiabetesEyeExam, "_has_retinal_finding_no_severity_in_prior_year")
@patch.object(CMS131v14DiabetesEyeExam, "_has_retinal_finding_with_severity_in_period")
@patch.object(CMS131v14DiabetesEyeExam, "_has_autonomous_eye_exam_in_period")
@patch.object(CMS131v14DiabetesEyeExam, "_has_retinal_exam_in_period_or_year_prior")
@patch.object(CMS131v14DiabetesEyeExam, "_has_retinal_exam_in_period")
@patch.object(CMS131v14DiabetesEyeExam, "_has_retinopathy_diagnosis_in_period")
def test_in_numerator_false_with_retinopathy_without_exam(
    mock_has_retinopathy: MagicMock,
    mock_exam_in_period_or_year_prior: MagicMock,
    mock_exam_in_lookback: MagicMock,
    mock_autonomous_exam: MagicMock,
    mock_severity_finding: MagicMock,
    mock_no_severity_prior: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
):
    """If retinopathy lacks a supporting exam, numerator should not pass."""
    mock_has_retinopathy.return_value = True
    mock_exam_in_period_or_year_prior.return_value = False
    mock_exam_in_lookback.return_value = False
    mock_autonomous_exam.return_value = False
    mock_severity_finding.return_value = False
    mock_no_severity_prior.return_value = False

    assert protocol_instance._in_numerator(mock_patient) is False


@patch.object(CMS131v14DiabetesEyeExam, "_has_retinal_finding_no_severity_in_prior_year")
@patch.object(CMS131v14DiabetesEyeExam, "_has_retinal_finding_with_severity_in_period")
@patch.object(CMS131v14DiabetesEyeExam, "_has_autonomous_eye_exam_in_period")
@patch.object(CMS131v14DiabetesEyeExam, "_has_retinal_exam_in_period_or_year_prior")
@patch.object(CMS131v14DiabetesEyeExam, "_has_retinal_exam_in_period")
@patch.object(CMS131v14DiabetesEyeExam, "_has_retinopathy_diagnosis_in_period")
def test_in_numerator_true_with_exam_in_measurement_or_prior_year(
    mock_has_retinopathy: MagicMock,
    mock_exam_in_period_or_year_prior: MagicMock,
    mock_exam_in_lookback: MagicMock,
    mock_autonomous_exam: MagicMock,
    mock_severity_finding: MagicMock,
    mock_no_severity_prior: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
):
    """Exam in measurement period or lookback year covers patients without retinopathy."""
    mock_has_retinopathy.return_value = False
    mock_exam_in_period_or_year_prior.return_value = False
    mock_exam_in_lookback.return_value = True
    mock_autonomous_exam.return_value = False
    mock_severity_finding.return_value = False
    mock_no_severity_prior.return_value = False

    assert protocol_instance._in_numerator(mock_patient) is True
    mock_exam_in_lookback.assert_called_once_with(mock_patient)


@patch.object(CMS131v14DiabetesEyeExam, "_has_retinal_finding_no_severity_in_prior_year")
@patch.object(CMS131v14DiabetesEyeExam, "_has_retinal_finding_with_severity_in_period")
@patch.object(CMS131v14DiabetesEyeExam, "_has_autonomous_eye_exam_in_period")
@patch.object(CMS131v14DiabetesEyeExam, "_has_retinal_exam_in_period_or_year_prior")
@patch.object(CMS131v14DiabetesEyeExam, "_has_retinal_exam_in_period")
@patch.object(CMS131v14DiabetesEyeExam, "_has_retinopathy_diagnosis_in_period")
def test_in_numerator_true_with_autonomous_eye_exam(
    mock_has_retinopathy: MagicMock,
    mock_exam_in_period_or_year_prior: MagicMock,
    mock_exam_in_lookback: MagicMock,
    mock_autonomous_exam: MagicMock,
    mock_severity_finding: MagicMock,
    mock_no_severity_prior: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
):
    """Autonomous AI exam path should independently satisfy numerator."""
    mock_has_retinopathy.return_value = False
    mock_exam_in_period_or_year_prior.return_value = False
    mock_exam_in_lookback.return_value = False
    mock_autonomous_exam.return_value = True
    mock_severity_finding.return_value = False
    mock_no_severity_prior.return_value = False

    assert protocol_instance._in_numerator(mock_patient) is True
    mock_autonomous_exam.assert_called_once_with(mock_patient)


@patch.object(CMS131v14DiabetesEyeExam, "_has_retinal_finding_no_severity_in_prior_year")
@patch.object(CMS131v14DiabetesEyeExam, "_has_retinal_finding_with_severity_in_period")
@patch.object(CMS131v14DiabetesEyeExam, "_has_autonomous_eye_exam_in_period")
@patch.object(CMS131v14DiabetesEyeExam, "_has_retinal_exam_in_period_or_year_prior")
@patch.object(CMS131v14DiabetesEyeExam, "_has_retinal_exam_in_period")
@patch.object(CMS131v14DiabetesEyeExam, "_has_retinopathy_diagnosis_in_period")
def test_in_numerator_true_with_retinopathy_severity_findings(
    mock_has_retinopathy: MagicMock,
    mock_exam_in_period_or_year_prior: MagicMock,
    mock_exam_in_lookback: MagicMock,
    mock_autonomous_exam: MagicMock,
    mock_severity_finding: MagicMock,
    mock_no_severity_prior: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
):
    """Retinal findings documenting severity in the period qualifies the patient."""
    mock_has_retinopathy.return_value = False
    mock_exam_in_period_or_year_prior.return_value = False
    mock_exam_in_lookback.return_value = False
    mock_autonomous_exam.return_value = False
    mock_severity_finding.return_value = True
    mock_no_severity_prior.return_value = False

    assert protocol_instance._in_numerator(mock_patient) is True
    mock_severity_finding.assert_called_once_with(mock_patient)


@patch.object(CMS131v14DiabetesEyeExam, "_has_retinal_finding_no_severity_in_prior_year")
@patch.object(CMS131v14DiabetesEyeExam, "_has_retinal_finding_with_severity_in_period")
@patch.object(CMS131v14DiabetesEyeExam, "_has_autonomous_eye_exam_in_period")
@patch.object(CMS131v14DiabetesEyeExam, "_has_retinal_exam_in_period_or_year_prior")
@patch.object(CMS131v14DiabetesEyeExam, "_has_retinal_exam_in_period")
@patch.object(CMS131v14DiabetesEyeExam, "_has_retinopathy_diagnosis_in_period")
def test_in_numerator_true_with_prior_year_no_retinopathy_documented(
    mock_has_retinopathy: MagicMock,
    mock_exam_in_period_or_year_prior: MagicMock,
    mock_exam_in_lookback: MagicMock,
    mock_autonomous_exam: MagicMock,
    mock_severity_finding: MagicMock,
    mock_no_severity_prior: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
):
    """Prior-year documentation of no retinopathy (both eyes) should satisfy numerator."""
    mock_has_retinopathy.return_value = False
    mock_exam_in_period_or_year_prior.return_value = False
    mock_exam_in_lookback.return_value = False
    mock_autonomous_exam.return_value = False
    mock_severity_finding.return_value = False
    mock_no_severity_prior.return_value = True

    assert protocol_instance._in_numerator(mock_patient) is True
    mock_no_severity_prior.assert_called_once_with(mock_patient)


@patch.object(CMS131v14DiabetesEyeExam, "_has_retinal_finding_no_severity_in_prior_year")
@patch.object(CMS131v14DiabetesEyeExam, "_has_retinal_finding_with_severity_in_period")
@patch.object(CMS131v14DiabetesEyeExam, "_has_autonomous_eye_exam_in_period")
@patch.object(CMS131v14DiabetesEyeExam, "_has_retinal_exam_in_period_or_year_prior")
@patch.object(CMS131v14DiabetesEyeExam, "_has_retinal_exam_in_period")
@patch.object(CMS131v14DiabetesEyeExam, "_has_retinopathy_diagnosis_in_period")
def test_in_numerator_false_when_no_criteria_met(
    mock_has_retinopathy: MagicMock,
    mock_exam_in_period_or_year_prior: MagicMock,
    mock_exam_in_lookback: MagicMock,
    mock_autonomous_exam: MagicMock,
    mock_severity_finding: MagicMock,
    mock_no_severity_prior: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
):
    """If every helper check fails, the numerator result should be False."""
    mock_has_retinopathy.return_value = False
    mock_exam_in_period_or_year_prior.return_value = False
    mock_exam_in_lookback.return_value = False
    mock_autonomous_exam.return_value = False
    mock_severity_finding.return_value = False
    mock_no_severity_prior.return_value = False

    assert protocol_instance._in_numerator(mock_patient) is False


@patch("canvas_sdk.effects.protocol_card.protocol_card.ProtocolCard.apply")
def test_create_satisfied_card(
    mock_apply: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
):
    """Test _create_satisfied_card creates card with SATISFIED status."""
    mock_apply.return_value = "SATISFIED_EFFECT"

    effect = protocol_instance._create_satisfied_card(mock_patient)
    assert effect == "SATISFIED_EFFECT"
    mock_apply.assert_called_once()


@patch.object(CMS131v14DiabetesEyeExam, "_get_diabetes_diagnosis_codes")
@patch("canvas_sdk.effects.protocol_card.protocol_card.ProtocolCard.apply")
def test_create_due_card(
    mock_apply: MagicMock,
    mock_get_codes: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
):
    """Test _create_due_card creates card with DUE status and recommendations."""
    mock_apply.return_value = "DUE_EFFECT"
    mock_get_codes.return_value = ["E11.9", "E11.21"]

    effect = protocol_instance._create_due_card(mock_patient)
    assert effect == "DUE_EFFECT"
    mock_apply.assert_called_once()
    mock_get_codes.assert_called_once_with(mock_patient)


@patch.object(CMS131v14DiabetesEyeExam, "_get_patient")
def test_compute_patient_not_found(
    mock_get_patient: MagicMock, protocol_instance: CMS131v14DiabetesEyeExam
):
    """Test compute returns empty list when patient not found."""
    mock_get_patient.return_value = (None, None)

    effects = protocol_instance.compute()
    assert effects == []


@patch.object(CMS131v14DiabetesEyeExam, "_create_not_applicable_card")
@patch.object(CMS131v14DiabetesEyeExam, "_should_remove_card")
@patch.object(CMS131v14DiabetesEyeExam, "_get_patient")
def test_compute_should_remove_card(
    mock_get_patient: MagicMock,
    mock_should_remove: MagicMock,
    mock_create_card: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
    mock_condition: Mock,
):
    """Test compute returns NOT_APPLICABLE card when should remove card."""
    mock_get_patient.return_value = (mock_patient, mock_condition)
    mock_should_remove.return_value = True
    mock_create_card.return_value = "NOT_APPLICABLE_CARD"

    effects = protocol_instance.compute()
    assert effects == ["NOT_APPLICABLE_CARD"]
    mock_create_card.assert_called_once_with(mock_patient)


@patch.object(CMS131v14DiabetesEyeExam, "_create_not_applicable_card")
@patch.object(CMS131v14DiabetesEyeExam, "_in_initial_population")
@patch.object(CMS131v14DiabetesEyeExam, "_should_remove_card")
@patch.object(CMS131v14DiabetesEyeExam, "_get_patient")
def test_compute_not_in_initial_population(
    mock_get_patient: MagicMock,
    mock_should_remove: MagicMock,
    mock_in_initial: MagicMock,
    mock_create_card: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
    mock_condition: Mock,
):
    """Test compute returns NOT_APPLICABLE card when not in initial population."""
    mock_get_patient.return_value = (mock_patient, mock_condition)
    mock_should_remove.return_value = False
    mock_in_initial.return_value = False
    mock_create_card.return_value = "NOT_APPLICABLE_CARD"

    effects = protocol_instance.compute()
    assert effects == ["NOT_APPLICABLE_CARD"]


@patch.object(CMS131v14DiabetesEyeExam, "_create_not_applicable_card")
@patch.object(CMS131v14DiabetesEyeExam, "_in_denominator")
@patch.object(CMS131v14DiabetesEyeExam, "_in_initial_population")
@patch.object(CMS131v14DiabetesEyeExam, "_should_remove_card")
@patch.object(CMS131v14DiabetesEyeExam, "_get_patient")
def test_compute_excluded_from_denominator(
    mock_get_patient: MagicMock,
    mock_should_remove: MagicMock,
    mock_in_initial: MagicMock,
    mock_in_denominator: MagicMock,
    mock_create_card: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
    mock_condition: Mock,
):
    """Test compute returns NOT_APPLICABLE card when excluded from denominator."""
    mock_get_patient.return_value = (mock_patient, mock_condition)
    mock_should_remove.return_value = False
    mock_in_initial.return_value = True
    mock_in_denominator.return_value = False
    mock_create_card.return_value = "NOT_APPLICABLE_CARD"

    effects = protocol_instance.compute()
    assert effects == ["NOT_APPLICABLE_CARD"]
