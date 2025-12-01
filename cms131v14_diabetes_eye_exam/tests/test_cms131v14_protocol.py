from datetime import date, datetime
from unittest.mock import MagicMock, Mock, patch

import arrow
import pytest
from cms131v14_diabetes_eye_exam.protocols.cms131v14_protocol import CMS131v14DiabetesEyeExam

from canvas_sdk.events import EventType
from canvas_sdk.v1.data import Patient
from canvas_sdk.v1.data.condition import Condition


@pytest.fixture
def mock_patient() -> Mock:
    """Create a mock patient."""
    patient = Mock(spec=Patient)
    patient.id = "patient-123"
    patient.first_name = "John"
    patient.last_name = "Doe"
    patient.birth_date = "1970-01-01"

    def age_at(date: datetime | date | arrow.Arrow | str) -> int:
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
def protocol_instance(mock_event: Mock, mock_timeframe: Mock) -> CMS131v14DiabetesEyeExam:
    """Create a protocol instance with mocked dependencies."""
    protocol = CMS131v14DiabetesEyeExam(mock_event)
    return protocol


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_get_patient_with_condition_created_event(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
    mock_condition: Mock,
) -> None:
    """Test _get_patient_and_condition returns patient and condition for CONDITION_CREATED event."""
    mock_condition.patient = mock_patient
    mock_condition_objects.filter.return_value.select_related.return_value.first.return_value = (
        mock_condition
    )

    patient, condition = protocol_instance._get_patient_and_condition()
    assert patient == mock_patient
    assert condition == mock_condition
    mock_condition_objects.filter.assert_called_once_with(id="condition-123")


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_get_patient_when_condition_not_found(
    mock_condition_objects: MagicMock, protocol_instance: CMS131v14DiabetesEyeExam
) -> None:
    """Test _get_patient_and_condition returns None when condition not found."""
    mock_condition_objects.filter.return_value.select_related.return_value.first.return_value = None

    patient, condition = protocol_instance._get_patient_and_condition()

    assert patient is None
    assert condition is None


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_is_condition_diabetes_returns_true(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_condition: Mock,
) -> None:
    """Test _is_condition_diabetes returns True for diabetes condition."""
    mock_condition_objects.filter.return_value.find.return_value.exists.return_value = True
    result = protocol_instance._is_condition_diabetes(mock_condition)
    assert result is True
    mock_condition_objects.filter.assert_called_once_with(id=mock_condition.id)


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_is_condition_diabetes_returns_false(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_condition: Mock,
) -> None:
    """Test _is_condition_diabetes returns False for non-diabetes condition."""
    mock_condition_objects.filter.return_value.find.return_value.exists.return_value = False
    result = protocol_instance._is_condition_diabetes(mock_condition)
    assert result is False


def test_should_remove_card_with_no_condition(
    protocol_instance: CMS131v14DiabetesEyeExam, mock_patient: Mock
) -> None:
    """Test _should_remove_card returns False when condition is None."""
    result = protocol_instance._should_remove_card(mock_patient, None)
    assert result is False


@patch.object(CMS131v14DiabetesEyeExam, "_is_condition_diabetes")
def test_should_remove_card_with_non_diabetes_condition(
    mock_is_diabetes: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
    mock_condition: Mock,
) -> None:
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
) -> None:
    """Test _should_remove_card returns True when diabetes entered in error and no other diabetes."""
    mock_condition.entered_in_error = True
    mock_is_diabetes.return_value = True
    mock_has_diabetes.return_value = False

    result = protocol_instance._should_remove_card(mock_patient, mock_condition)
    assert result is True
    mock_has_diabetes.assert_called_once_with(mock_patient)


def test_in_initial_population_age_too_young(
    protocol_instance: CMS131v14DiabetesEyeExam, mock_patient: Mock
) -> None:
    """Test _in_initial_population returns False for age < 18."""
    result = protocol_instance._in_initial_population(mock_patient, age=17)
    assert result is False


def test_in_initial_population_age_too_old(
    protocol_instance: CMS131v14DiabetesEyeExam, mock_patient: Mock
) -> None:
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
) -> None:
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
) -> None:
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
) -> None:
    """Test _has_diabetes_diagnosis returns True when diabetes exists."""
    mock_condition_objects.for_patient.return_value.find.return_value.active.return_value.filter.return_value.exists.return_value = True

    result = protocol_instance._has_diabetes_diagnosis(mock_patient)
    assert result is True
    mock_condition_objects.for_patient.assert_called_once_with(mock_patient.id)


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_diabetes_diagnosis_false(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_diabetes_diagnosis returns False when no diabetes."""
    mock_condition_objects.for_patient.return_value.find.return_value.active.return_value.filter.return_value.exists.return_value = False

    result = protocol_instance._has_diabetes_diagnosis(mock_patient)
    assert result is False


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_diabetes_diagnosis_overlapping_period_true(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_diabetes_diagnosis_overlapping_period returns True."""
    mock_condition_objects.for_patient.return_value.find.return_value.committed.return_value.filter.return_value.filter.return_value.exists.return_value = True

    result = protocol_instance._has_diabetes_diagnosis_overlapping_period(mock_patient)
    assert result is True


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_diabetes_diagnosis_overlapping_period_false(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_diabetes_diagnosis_overlapping_period returns False."""
    mock_condition_objects.for_patient.return_value.find.return_value.committed.return_value.filter.return_value.filter.return_value.exists.return_value = False

    result = protocol_instance._has_diabetes_diagnosis_overlapping_period(mock_patient)
    assert result is False


@patch("canvas_sdk.v1.data.encounter.Encounter.objects")
def test_has_eligible_encounter_in_period_has_office_visit(
    mock_encounter_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_eligible_encounter_in_period returns True when office visit encounter exists."""
    mock_encounter_objects.filter.return_value.exists.return_value = True

    result = protocol_instance._has_eligible_encounter_in_period(mock_patient)
    assert result is True


@patch("canvas_sdk.v1.data.encounter.Encounter.objects")
@patch("canvas_sdk.v1.data.claim_line_item.ClaimLineItem.objects")
def test_has_eligible_encounter_in_period_has_preventive_care_claim(
    mock_claim_objects: MagicMock,
    mock_encounter_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_eligible_encounter_in_period returns True when preventive care claim exists."""
    # No office visit encounters
    mock_encounter_objects.filter.return_value.exists.return_value = True

    # Has preventive care claim
    mock_claim = Mock()
    mock_claim.proc_code = "99385"  # Preventive care established patient
    mock_claim_objects.filter.return_value.exists.return_value = True
    mock_claim_objects.filter.return_value.first.return_value = mock_claim

    result = protocol_instance._has_eligible_encounter_in_period(mock_patient)
    assert result is True


@patch("canvas_sdk.v1.data.encounter.Encounter.objects")
@patch("canvas_sdk.v1.data.claim_line_item.ClaimLineItem.objects")
def test_has_eligible_encounter_in_period_false(
    mock_claim_objects: MagicMock,
    mock_encounter_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_eligible_encounter_in_period returns False when no eligible encounters."""
    mock_encounter_objects.filter.return_value.first.return_value = None
    mock_claim_objects.filter.return_value.first.return_value = None

    result = protocol_instance._has_eligible_encounter_in_period(mock_patient)
    assert result is False


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_hospice_care_in_period_has_condition(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_hospice_care_in_period returns True for hospice diagnosis."""
    mock_condition_objects.for_patient.return_value.find.return_value.active.return_value.filter.return_value.exists.return_value = True

    result = protocol_instance._has_hospice_care_in_period(mock_patient)
    assert result is True


@patch("canvas_sdk.v1.data.observation.Observation.objects")
@patch("canvas_sdk.v1.data.encounter.Encounter.objects")
@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_hospice_care_in_period_has_discharge_observation(
    mock_condition_objects: MagicMock,
    mock_encounter_objects: MagicMock,
    mock_observation_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_hospice_care_in_period returns True for discharge to hospice observation."""
    # No hospice diagnosis
    mock_condition_objects.for_patient.return_value.find.return_value.active.return_value.filter.return_value.exists.return_value = False

    # No hospice encounter
    mock_encounter_objects.filter.return_value.exists.return_value = False

    # Has discharge to hospice observation
    mock_observation_objects.for_patient.return_value.filter.return_value.exists.return_value = True

    result = protocol_instance._has_hospice_care_in_period(mock_patient)
    assert result is True


@patch("canvas_sdk.v1.data.claim_line_item.ClaimLineItem.objects")
@patch("canvas_sdk.v1.data.observation.Observation.objects")
@patch("canvas_sdk.v1.data.encounter.Encounter.objects")
@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_hospice_care_in_period_has_claim(
    mock_condition_objects: MagicMock,
    mock_encounter_objects: MagicMock,
    mock_observation_objects: MagicMock,
    mock_claim_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_hospice_care_in_period returns True for hospice claim."""
    # No hospice diagnosis
    mock_condition_objects.for_patient.return_value.find.return_value.active.return_value.filter.return_value.exists.return_value = False

    # No hospice encounter
    mock_encounter_objects.filter.return_value.exists.return_value = False

    # No discharge to hospice observation (first call for discharge)
    # Has hospice assessment (second call for assessment)
    mock_observation_objects.for_patient.return_value.filter.return_value.exists.side_effect = [
        False,
        False,
    ]

    # Has hospice claim
    mock_claim = Mock()
    mock_claim.proc_code = "99377"
    mock_claim_objects.filter.return_value.exists.return_value = True
    mock_claim_objects.filter.return_value.first.return_value = mock_claim

    result = protocol_instance._has_hospice_care_in_period(mock_patient)
    assert result is True


@patch("canvas_sdk.v1.data.claim_line_item.ClaimLineItem.objects")
@patch("canvas_sdk.v1.data.observation.Observation.objects")
@patch("canvas_sdk.v1.data.encounter.Encounter.objects")
@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_hospice_care_in_period_false(
    mock_condition_objects: MagicMock,
    mock_encounter_objects: MagicMock,
    mock_observation_objects: MagicMock,
    mock_claim_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_hospice_care_in_period returns False when no hospice indicators exist."""
    # No hospice diagnosis
    mock_condition_objects.for_patient.return_value.find.return_value.active.return_value.filter.return_value.exists.return_value = False

    # No hospice encounter
    mock_encounter_objects.filter.return_value.exists.return_value = False

    # No observations (discharge or assessment)
    mock_observation_objects.for_patient.return_value.filter.return_value.exists.return_value = (
        False
    )

    # No hospice claim
    mock_claim_objects.filter.return_value.first.return_value = None

    result = protocol_instance._has_hospice_care_in_period(mock_patient)
    assert result is False


def test_is_age_66_plus_with_frailty_age_less_than_66(
    protocol_instance: CMS131v14DiabetesEyeExam, mock_patient: Mock
) -> None:
    """Test _is_age_66_plus_with_frailty returns False for age < 66."""
    result = protocol_instance._is_age_66_plus_with_frailty(mock_patient, age=65)
    assert result is False


def test_is_age_66_plus_with_frailty_true(
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _is_age_66_plus_with_frailty returns True when age 66+ with frailty."""
    # Mock one of the frailty check methods to return True
    with patch.object(protocol_instance, "_has_frailty_device_orders", return_value=True):
        result = protocol_instance._is_age_66_plus_with_frailty(mock_patient, age=70)
        assert result is True


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_advanced_illness_or_dementia_meds_has_advanced_illness(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_advanced_illness_or_dementia_meds returns True for advanced illness."""
    mock_condition_objects.for_patient.return_value.active.return_value.find.return_value.exists.return_value = True

    result = protocol_instance._has_advanced_illness_or_dementia_meds(mock_patient)
    assert result is True


@patch("canvas_sdk.v1.data.medication.Medication.objects")
@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_advanced_illness_or_dementia_meds_has_dementia_meds(
    mock_condition_objects: MagicMock,
    mock_medication_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_advanced_illness_or_dementia_meds returns True for dementia meds."""
    # No advanced illness
    mock_condition_objects.for_patient.return_value.active.return_value.find.return_value.exists.return_value = False

    # Has dementia meds
    mock_medication_objects.for_patient.return_value.active.return_value.find.return_value.filter.return_value.exists.return_value = True

    result = protocol_instance._has_advanced_illness_or_dementia_meds(mock_patient)
    assert result is True


@patch("canvas_sdk.v1.data.medication.Medication.objects")
@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_advanced_illness_or_dementia_meds_false(
    mock_condition_objects: MagicMock,
    mock_medication_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_advanced_illness_or_dementia_meds returns False when neither exists."""
    # Mock the debug query
    mock_condition_objects.for_patient.return_value.find.return_value.filter.return_value.committed.return_value.exists.return_value = False

    # Mock the actual advanced illness check
    mock_condition_objects.for_patient.return_value.find.return_value.filter.return_value.filter.return_value.exists.return_value = False

    # Mock the dementia meds check
    mock_medication_objects.for_patient.return_value.committed.return_value.find.return_value.filter.return_value.exists.return_value = False

    result = protocol_instance._has_advanced_illness_or_dementia_meds(mock_patient)
    assert result is False


def test_is_age_66_plus_in_nursing_home_age_less_than_66(
    protocol_instance: CMS131v14DiabetesEyeExam, mock_patient: Mock
) -> None:
    """Test _is_age_66_plus_in_nursing_home returns False for age < 66."""
    result = protocol_instance._is_age_66_plus_in_nursing_home(mock_patient, age=65)
    assert result is False


@patch("canvas_sdk.v1.data.claim_line_item.ClaimLineItem.objects")
def test_is_age_66_plus_in_nursing_home_true(
    mock_claim_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
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
) -> None:
    """Test _is_age_66_plus_in_nursing_home returns False when no nursing home claim."""
    mock_claim_objects.filter.return_value.first.return_value = None

    result = protocol_instance._is_age_66_plus_in_nursing_home(mock_patient, age=70)
    assert result is False


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_palliative_care_in_period_has_condition(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_palliative_care_in_period returns True for palliative condition."""
    mock_condition_objects.for_patient.return_value.active.return_value.find.return_value.exists.return_value = True

    result = protocol_instance._has_palliative_care_in_period(mock_patient)
    assert result is True


@patch("canvas_sdk.v1.data.claim_line_item.ClaimLineItem.objects")
@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_palliative_care_in_period_has_claim(
    mock_condition_objects: MagicMock,
    mock_claim_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_palliative_care_in_period returns True for palliative claim."""
    # No palliative condition
    mock_condition_objects.for_patient.return_value.active.return_value.find.return_value.exists.return_value = False

    # Has palliative claim
    mock_claim = Mock()
    mock_claim.proc_code = "M1141"
    mock_claim_objects.filter.return_value.exists.return_value = True
    mock_claim_objects.filter.return_value.first.return_value = mock_claim

    result = protocol_instance._has_palliative_care_in_period(mock_patient)
    assert result is True


@patch("canvas_sdk.v1.data.claim_line_item.ClaimLineItem.objects")
@patch("canvas_sdk.v1.data.encounter.Encounter.objects")
@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_palliative_care_in_period_false(
    mock_condition_objects: MagicMock,
    mock_encounter_objects: MagicMock,
    mock_claim_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_palliative_care_in_period returns False when neither exists."""
    mock_condition_objects.for_patient.return_value.find.return_value.active.return_value.filter.return_value.exists.return_value = False
    mock_encounter_objects.filter.return_value.exists.return_value = False
    mock_claim_objects.filter.return_value.first.return_value = None

    result = protocol_instance._has_palliative_care_in_period(mock_patient)
    assert result is False


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_bilateral_absence_of_eyes_true(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_bilateral_absence_of_eyes returns True when condition exists."""
    mock_condition_objects.for_patient.return_value.active.return_value.filter.return_value.filter.return_value.exists.return_value = True

    result = protocol_instance._has_bilateral_absence_of_eyes(mock_patient)
    assert result is True


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_bilateral_absence_of_eyes_false(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_bilateral_absence_of_eyes returns False when condition doesn't exist."""
    mock_condition_objects.for_patient.return_value.active.return_value.filter.return_value.filter.return_value.exists.return_value = False

    result = protocol_instance._has_bilateral_absence_of_eyes(mock_patient)
    assert result is False


@patch.object(CMS131v14DiabetesEyeExam, "_has_hospice_care_in_period")
def test_in_denominator_excluded_by_hospice(
    mock_has_hospice: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
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
) -> None:
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
) -> None:
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
) -> None:
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
) -> None:
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
) -> None:
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
) -> None:
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
) -> None:
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
) -> None:
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
) -> None:
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
) -> None:
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
) -> None:
    """Test _create_due_card creates card with DUE status and recommendations."""
    mock_apply.return_value = "DUE_EFFECT"
    mock_get_codes.return_value = ["E11.9", "E11.21"]

    effect = protocol_instance._create_due_card(mock_patient)
    assert effect == "DUE_EFFECT"
    mock_apply.assert_called_once()
    mock_get_codes.assert_called_once_with(mock_patient)


@patch.object(CMS131v14DiabetesEyeExam, "_get_patient_and_condition")
def test_compute_patient_not_found(
    mock_get_patient: MagicMock, protocol_instance: CMS131v14DiabetesEyeExam
) -> None:
    """Test compute returns empty list when patient not found."""
    mock_get_patient.return_value = (None, None)

    effects = protocol_instance.compute()
    assert effects == []


@patch.object(CMS131v14DiabetesEyeExam, "_create_not_applicable_card")
@patch.object(CMS131v14DiabetesEyeExam, "_should_remove_card")
@patch.object(CMS131v14DiabetesEyeExam, "_get_patient_and_condition")
def test_compute_should_remove_card(
    mock_get_patient: MagicMock,
    mock_should_remove: MagicMock,
    mock_create_card: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
    mock_condition: Mock,
) -> None:
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
@patch.object(CMS131v14DiabetesEyeExam, "_get_patient_and_condition")
def test_compute_not_in_initial_population(
    mock_get_patient: MagicMock,
    mock_should_remove: MagicMock,
    mock_in_initial: MagicMock,
    mock_create_card: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
    mock_condition: Mock,
) -> None:
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
@patch.object(CMS131v14DiabetesEyeExam, "_get_patient_and_condition")
def test_compute_excluded_from_denominator(
    mock_get_patient: MagicMock,
    mock_should_remove: MagicMock,
    mock_in_initial: MagicMock,
    mock_in_denominator: MagicMock,
    mock_create_card: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
    mock_condition: Mock,
) -> None:
    """Test compute returns NOT_APPLICABLE card when excluded from denominator."""
    mock_get_patient.return_value = (mock_patient, mock_condition)
    mock_should_remove.return_value = False
    mock_in_initial.return_value = True
    mock_in_denominator.return_value = False
    mock_create_card.return_value = "NOT_APPLICABLE_CARD"

    effects = protocol_instance.compute()
    assert effects == ["NOT_APPLICABLE_CARD"]


@patch.object(CMS131v14DiabetesEyeExam, "_get_patient_and_condition")
def test_compute_exception_handling(
    mock_get_patient: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
) -> None:
    """Test compute handles exceptions gracefully."""
    mock_get_patient.side_effect = Exception("Test exception")

    effects = protocol_instance.compute()
    assert effects == []


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_get_patient_and_condition_no_patient(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_condition: Mock,
) -> None:
    """Test _get_patient_and_condition when condition has no patient."""
    mock_condition.patient = None
    mock_condition_objects.filter.return_value.select_related.return_value.first.return_value = (
        mock_condition
    )

    patient, condition = protocol_instance._get_patient_and_condition()
    assert patient is None
    assert condition is None


@patch.object(CMS131v14DiabetesEyeExam, "_has_diabetes_diagnosis")
@patch.object(CMS131v14DiabetesEyeExam, "_is_condition_diabetes")
def test_should_remove_card_diabetes_entered_in_error_with_other_diabetes(
    mock_is_diabetes: MagicMock,
    mock_has_diabetes: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
    mock_condition: Mock,
) -> None:
    """Test _should_remove_card returns False when diabetes entered in error but other diabetes exists."""
    mock_condition.entered_in_error = True
    mock_is_diabetes.return_value = True
    mock_has_diabetes.return_value = True

    result = protocol_instance._should_remove_card(mock_patient, mock_condition)
    assert result is False


@patch.object(CMS131v14DiabetesEyeExam, "_is_condition_diabetes")
def test_should_remove_card_exception(
    mock_is_diabetes: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
    mock_condition: Mock,
) -> None:
    """Test _should_remove_card handles exceptions."""
    mock_is_diabetes.side_effect = Exception("Test exception")

    result = protocol_instance._should_remove_card(mock_patient, mock_condition)
    assert result is False


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_is_condition_diabetes_exception(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_condition: Mock,
) -> None:
    """Test _is_condition_diabetes handles exceptions."""
    mock_condition_objects.filter.side_effect = Exception("Test exception")

    result = protocol_instance._is_condition_diabetes(mock_condition)
    assert result is False


@patch("canvas_sdk.v1.data.encounter.Encounter.objects")
def test_has_eligible_encounter_in_period_exception(
    mock_encounter_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_eligible_encounter_in_period handles exceptions."""
    mock_encounter_objects.filter.side_effect = Exception("Test exception")

    result = protocol_instance._has_eligible_encounter_in_period(mock_patient)
    assert result is False


@patch("canvas_sdk.v1.data.referral.ReferralReport.objects")
def test_referral_report_exists_exception(
    mock_referral_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _referral_report_exists handles exceptions."""
    mock_referral_objects.filter.side_effect = Exception("Test exception")

    result = protocol_instance._referral_report_exists(
        mock_patient,
        arrow.get("2024-01-01").datetime,
        arrow.get("2024-12-31").datetime,
    )
    assert result is False


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_get_diabetes_diagnosis_codes_exception(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _get_diabetes_diagnosis_codes handles exceptions."""
    mock_condition_objects.for_patient.side_effect = Exception("Test exception")

    result = protocol_instance._get_diabetes_diagnosis_codes(mock_patient)
    assert result == []


def test_get_value_set_codes(
    protocol_instance: CMS131v14DiabetesEyeExam,
) -> None:
    """Test _get_value_set_codes retrieves codes from value set attributes."""

    class MockValueSet:
        SNOMEDCT = {"123456", "789012"}
        ICD10CM = {"E119"}

    codes = protocol_instance._get_value_set_codes(MockValueSet, "SNOMEDCT", "ICD10CM")
    assert "123456" in codes
    assert "789012" in codes
    assert "E119" in codes


def test_get_value_set_codes_no_attributes(
    protocol_instance: CMS131v14DiabetesEyeExam,
) -> None:
    """Test _get_value_set_codes returns empty set when no attributes exist."""

    class MockValueSet:
        pass

    codes = protocol_instance._get_value_set_codes(MockValueSet, "SNOMEDCT")
    assert codes == set()


@patch.object(CMS131v14DiabetesEyeExam, "_has_frailty_device_observations")
@patch.object(CMS131v14DiabetesEyeExam, "_has_frailty_device_orders")
def test_is_age_66_plus_with_frailty_device_observations(
    mock_device_orders: MagicMock,
    mock_device_observations: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _is_age_66_plus_with_frailty returns True for device observations."""
    mock_device_orders.return_value = False
    mock_device_observations.return_value = True

    result = protocol_instance._is_age_66_plus_with_frailty(mock_patient, age=70)
    assert result is True


@patch.object(CMS131v14DiabetesEyeExam, "_has_frailty_symptoms")
@patch.object(CMS131v14DiabetesEyeExam, "_has_frailty_encounters")
@patch.object(CMS131v14DiabetesEyeExam, "_has_frailty_diagnoses")
@patch.object(CMS131v14DiabetesEyeExam, "_has_frailty_device_observations")
@patch.object(CMS131v14DiabetesEyeExam, "_has_frailty_device_orders")
def test_is_age_66_plus_with_frailty_all_checks_false(
    mock_device_orders: MagicMock,
    mock_device_observations: MagicMock,
    mock_frailty_diagnoses: MagicMock,
    mock_frailty_encounters: MagicMock,
    mock_frailty_symptoms: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _is_age_66_plus_with_frailty returns False when all checks fail."""
    mock_device_orders.return_value = False
    mock_device_observations.return_value = False
    mock_frailty_diagnoses.return_value = False
    mock_frailty_encounters.return_value = False
    mock_frailty_symptoms.return_value = False

    result = protocol_instance._is_age_66_plus_with_frailty(mock_patient, age=70)
    assert result is False


@patch.object(CMS131v14DiabetesEyeExam, "_has_frailty_device_orders")
def test_is_age_66_plus_with_frailty_exception(
    mock_device_orders: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _is_age_66_plus_with_frailty handles exceptions."""
    mock_device_orders.side_effect = Exception("Test exception")

    result = protocol_instance._is_age_66_plus_with_frailty(mock_patient, age=70)
    assert result is False


@patch("canvas_sdk.v1.data.observation.Observation.objects")
def test_has_frailty_device_observations_exception(
    mock_observation_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_frailty_device_observations handles exceptions."""
    mock_observation_objects.for_patient.side_effect = Exception("Test exception")

    result = protocol_instance._has_frailty_device_observations(mock_patient)
    assert result is False


@patch.object(CMS131v14DiabetesEyeExam, "_observation_exists")
def test_has_retinal_finding_with_severity_exception(
    mock_observation_exists: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_retinal_finding_with_severity handles exceptions."""
    mock_observation_exists.side_effect = Exception("Test exception")

    result = protocol_instance._has_retinal_finding_with_severity_in_period(mock_patient)
    assert result is False


@patch.object(CMS131v14DiabetesEyeExam, "_observation_exists")
def test_has_retinal_finding_no_severity_in_prior_year_exception(
    mock_observation_exists: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_retinal_finding_no_severity_in_prior_year handles exceptions."""
    mock_observation_exists.side_effect = Exception("Test exception")

    result = protocol_instance._has_retinal_finding_no_severity_in_prior_year(mock_patient)
    assert result is False


@patch("canvas_sdk.v1.data.encounter.Encounter.objects")
def test_is_age_66_plus_in_nursing_home_via_encounter(
    mock_encounter_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _is_age_66_plus_in_nursing_home returns True when encounter exists."""
    with patch("canvas_sdk.v1.data.claim_line_item.ClaimLineItem.objects") as mock_claim_objects:
        mock_claim_objects.filter.return_value.first.return_value = None
        mock_encounter_objects.filter.return_value.exists.return_value = True

        result = protocol_instance._is_age_66_plus_in_nursing_home(mock_patient, age=70)
        assert result is True


@patch("canvas_sdk.v1.data.encounter.Encounter.objects")
def test_is_age_66_plus_in_nursing_home_exception(
    mock_encounter_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _is_age_66_plus_in_nursing_home handles exceptions."""
    mock_encounter_objects.filter.side_effect = Exception("Test exception")

    result = protocol_instance._is_age_66_plus_in_nursing_home(mock_patient, age=70)
    assert result is False


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_palliative_care_in_period_exception(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_palliative_care_in_period handles exceptions."""
    mock_condition_objects.for_patient.side_effect = Exception("Test exception")

    result = protocol_instance._has_palliative_care_in_period(mock_patient)
    assert result is False


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_bilateral_absence_of_eyes_exception(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_bilateral_absence_of_eyes handles exceptions."""
    mock_condition_objects.for_patient.side_effect = Exception("Test exception")

    result = protocol_instance._has_bilateral_absence_of_eyes(mock_patient)
    assert result is False


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_retinopathy_diagnosis_in_period_exception(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_retinopathy_diagnosis_in_period handles exceptions."""
    mock_condition_objects.for_patient.side_effect = Exception("Test exception")

    result = protocol_instance._has_retinopathy_diagnosis_in_period(mock_patient)
    assert result is False


@patch.object(CMS131v14DiabetesEyeExam, "_referral_report_exists")
def test_has_retinal_exam_in_period_exception(
    mock_referral_exists: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_retinal_exam_in_period handles exceptions."""
    mock_referral_exists.side_effect = Exception("Test exception")

    result = protocol_instance._has_retinal_exam_in_period(mock_patient)
    assert result is False


@patch.object(CMS131v14DiabetesEyeExam, "_referral_report_exists")
def test_has_retinal_exam_in_period_or_year_prior_exception(
    mock_referral_exists: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_retinal_exam_in_period_or_year_prior handles exceptions."""
    mock_referral_exists.side_effect = Exception("Test exception")

    result = protocol_instance._has_retinal_exam_in_period_or_year_prior(mock_patient)
    assert result is False


@patch("canvas_sdk.v1.data.observation.Observation.objects")
def test_observation_exists_exception(
    mock_observation_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _observation_exists handles exceptions."""
    mock_observation_objects.for_patient.side_effect = Exception("Test exception")

    result = protocol_instance._observation_exists(
        mock_patient,
        "45755-6",
        {"373066001"},
        arrow.get("2024-01-01").datetime,
        arrow.get("2024-12-31").datetime,
    )
    assert result is False


@patch.object(CMS131v14DiabetesEyeExam, "_observation_exists")
def test_has_autonomous_eye_exam_in_period_exception(
    mock_observation_exists: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_autonomous_eye_exam_in_period handles exceptions."""
    mock_observation_exists.side_effect = Exception("Test exception")

    result = protocol_instance._has_autonomous_eye_exam_in_period(mock_patient)
    assert result is False


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_diabetes_diagnosis_exception(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_diabetes_diagnosis handles exceptions."""
    mock_condition_objects.for_patient.side_effect = Exception("Test exception")

    result = protocol_instance._has_diabetes_diagnosis(mock_patient)
    assert result is False


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_diabetes_diagnosis_overlapping_period_exception(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_diabetes_diagnosis_overlapping_period handles exceptions."""
    mock_condition_objects.for_patient.side_effect = Exception("Test exception")

    result = protocol_instance._has_diabetes_diagnosis_overlapping_period(mock_patient)
    assert result is False


@patch.object(CMS131v14DiabetesEyeExam, "_has_bilateral_absence_of_eyes")
@patch.object(CMS131v14DiabetesEyeExam, "_has_palliative_care_in_period")
@patch.object(CMS131v14DiabetesEyeExam, "_is_age_66_plus_in_nursing_home")
@patch.object(CMS131v14DiabetesEyeExam, "_has_advanced_illness_or_dementia_meds")
@patch.object(CMS131v14DiabetesEyeExam, "_is_age_66_plus_with_frailty")
@patch.object(CMS131v14DiabetesEyeExam, "_has_hospice_care_in_period")
def test_in_denominator_excluded_by_nursing_home(
    mock_has_hospice: MagicMock,
    mock_is_frailty: MagicMock,
    mock_has_advanced_illness: MagicMock,
    mock_is_nursing_home: MagicMock,
    mock_has_palliative: MagicMock,
    mock_has_bilateral: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _in_denominator returns False when patient is age 66+ in nursing home."""
    mock_has_hospice.return_value = False
    mock_is_frailty.return_value = False
    mock_has_advanced_illness.return_value = False
    mock_is_nursing_home.return_value = True
    mock_has_palliative.return_value = False
    mock_has_bilateral.return_value = False

    result = protocol_instance._in_denominator(mock_patient, age=70)
    assert result is False


@patch.object(CMS131v14DiabetesEyeExam, "_has_bilateral_absence_of_eyes")
@patch.object(CMS131v14DiabetesEyeExam, "_has_palliative_care_in_period")
@patch.object(CMS131v14DiabetesEyeExam, "_is_age_66_plus_in_nursing_home")
@patch.object(CMS131v14DiabetesEyeExam, "_has_advanced_illness_or_dementia_meds")
@patch.object(CMS131v14DiabetesEyeExam, "_is_age_66_plus_with_frailty")
@patch.object(CMS131v14DiabetesEyeExam, "_has_hospice_care_in_period")
def test_in_denominator_excluded_by_palliative_care(
    mock_has_hospice: MagicMock,
    mock_is_frailty: MagicMock,
    mock_has_advanced_illness: MagicMock,
    mock_is_nursing_home: MagicMock,
    mock_has_palliative: MagicMock,
    mock_has_bilateral: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _in_denominator returns False when patient has palliative care."""
    mock_has_hospice.return_value = False
    mock_is_frailty.return_value = False
    mock_has_advanced_illness.return_value = False
    mock_is_nursing_home.return_value = False
    mock_has_palliative.return_value = True
    mock_has_bilateral.return_value = False

    result = protocol_instance._in_denominator(mock_patient, age=50)
    assert result is False


@patch.object(CMS131v14DiabetesEyeExam, "_has_bilateral_absence_of_eyes")
@patch.object(CMS131v14DiabetesEyeExam, "_has_palliative_care_in_period")
@patch.object(CMS131v14DiabetesEyeExam, "_is_age_66_plus_in_nursing_home")
@patch.object(CMS131v14DiabetesEyeExam, "_has_advanced_illness_or_dementia_meds")
@patch.object(CMS131v14DiabetesEyeExam, "_is_age_66_plus_with_frailty")
@patch.object(CMS131v14DiabetesEyeExam, "_has_hospice_care_in_period")
def test_in_denominator_excluded_by_bilateral_absence(
    mock_has_hospice: MagicMock,
    mock_is_frailty: MagicMock,
    mock_has_advanced_illness: MagicMock,
    mock_is_nursing_home: MagicMock,
    mock_has_palliative: MagicMock,
    mock_has_bilateral: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _in_denominator returns False when patient has bilateral absence of eyes."""
    mock_has_hospice.return_value = False
    mock_is_frailty.return_value = False
    mock_has_advanced_illness.return_value = False
    mock_is_nursing_home.return_value = False
    mock_has_palliative.return_value = False
    mock_has_bilateral.return_value = True

    result = protocol_instance._in_denominator(mock_patient, age=50)
    assert result is False


@patch.object(CMS131v14DiabetesEyeExam, "_has_frailty_symptoms")
@patch.object(CMS131v14DiabetesEyeExam, "_has_frailty_encounters")
@patch.object(CMS131v14DiabetesEyeExam, "_has_frailty_diagnoses")
@patch.object(CMS131v14DiabetesEyeExam, "_has_frailty_device_observations")
@patch.object(CMS131v14DiabetesEyeExam, "_has_frailty_device_orders")
def test_is_age_66_plus_with_frailty_diagnoses(
    mock_device_orders: MagicMock,
    mock_device_observations: MagicMock,
    mock_frailty_diagnoses: MagicMock,
    mock_frailty_encounters: MagicMock,
    mock_frailty_symptoms: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _is_age_66_plus_with_frailty returns True for frailty diagnoses."""
    mock_device_orders.return_value = False
    mock_device_observations.return_value = False
    mock_frailty_diagnoses.return_value = True
    mock_frailty_encounters.return_value = False
    mock_frailty_symptoms.return_value = False

    result = protocol_instance._is_age_66_plus_with_frailty(mock_patient, age=70)
    assert result is True


@patch.object(CMS131v14DiabetesEyeExam, "_has_frailty_symptoms")
@patch.object(CMS131v14DiabetesEyeExam, "_has_frailty_encounters")
@patch.object(CMS131v14DiabetesEyeExam, "_has_frailty_diagnoses")
@patch.object(CMS131v14DiabetesEyeExam, "_has_frailty_device_observations")
@patch.object(CMS131v14DiabetesEyeExam, "_has_frailty_device_orders")
def test_is_age_66_plus_with_frailty_encounters(
    mock_device_orders: MagicMock,
    mock_device_observations: MagicMock,
    mock_frailty_diagnoses: MagicMock,
    mock_frailty_encounters: MagicMock,
    mock_frailty_symptoms: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _is_age_66_plus_with_frailty returns True for frailty encounters."""
    mock_device_orders.return_value = False
    mock_device_observations.return_value = False
    mock_frailty_diagnoses.return_value = False
    mock_frailty_encounters.return_value = True
    mock_frailty_symptoms.return_value = False

    result = protocol_instance._is_age_66_plus_with_frailty(mock_patient, age=70)
    assert result is True


@patch.object(CMS131v14DiabetesEyeExam, "_has_frailty_symptoms")
@patch.object(CMS131v14DiabetesEyeExam, "_has_frailty_encounters")
@patch.object(CMS131v14DiabetesEyeExam, "_has_frailty_diagnoses")
@patch.object(CMS131v14DiabetesEyeExam, "_has_frailty_device_observations")
@patch.object(CMS131v14DiabetesEyeExam, "_has_frailty_device_orders")
def test_is_age_66_plus_with_frailty_symptoms(
    mock_device_orders: MagicMock,
    mock_device_observations: MagicMock,
    mock_frailty_diagnoses: MagicMock,
    mock_frailty_encounters: MagicMock,
    mock_frailty_symptoms: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _is_age_66_plus_with_frailty returns True for frailty symptoms."""
    mock_device_orders.return_value = False
    mock_device_observations.return_value = False
    mock_frailty_diagnoses.return_value = False
    mock_frailty_encounters.return_value = False
    mock_frailty_symptoms.return_value = True

    result = protocol_instance._is_age_66_plus_with_frailty(mock_patient, age=70)
    assert result is True


@patch("canvas_sdk.v1.data.device.Device.objects")
@patch("canvas_sdk.v1.data.claim_line_item.ClaimLineItem.objects")
@patch("cms131v14_diabetes_eye_exam.protocols.cms131v14_protocol.FrailtyDevice")
def test_has_frailty_device_orders_via_dme_claim(
    mock_frailty_device: MagicMock,
    mock_claim_objects: MagicMock,
    mock_device_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_frailty_device_orders returns True when DME claim exists."""
    mock_frailty_device.HCPCSLEVELII = {"E0160", "E0161"}
    mock_claim_objects.filter.return_value.exists.return_value = True
    mock_device_objects.filter.return_value.exists.return_value = False

    result = protocol_instance._has_frailty_device_orders(mock_patient)
    assert result is True


@patch("canvas_sdk.v1.data.device.Device.objects")
@patch("canvas_sdk.v1.data.claim_line_item.ClaimLineItem.objects")
@patch("cms131v14_diabetes_eye_exam.protocols.cms131v14_protocol.FrailtyDevice")
def test_has_frailty_device_orders_no_hcpcs_attribute(
    mock_frailty_device: MagicMock,
    mock_claim_objects: MagicMock,
    mock_device_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_frailty_device_orders handles case when HCPCSLEVELII attribute doesn't exist."""
    delattr(mock_frailty_device, "HCPCSLEVELII") if hasattr(
        mock_frailty_device, "HCPCSLEVELII"
    ) else None
    mock_device_objects.filter.return_value.exists.return_value = True

    result = protocol_instance._has_frailty_device_orders(mock_patient)
    assert result is True


@patch("canvas_sdk.v1.data.observation.Observation.objects")
def test_has_frailty_device_observations_no_snomed_codes(
    mock_observation_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_frailty_device_observations returns False when no SNOMED codes available."""
    with patch.object(protocol_instance, "_get_value_set_codes", return_value=set()):
        result = protocol_instance._has_frailty_device_observations(mock_patient)
        assert result is False


@patch("canvas_sdk.v1.data.observation.Observation.objects")
def test_has_frailty_device_observations_with_observation(
    mock_observation_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_frailty_device_observations returns True when observation exists."""
    with patch.object(protocol_instance, "_get_value_set_codes", return_value={"123456"}):
        mock_observation_objects.for_patient.return_value.filter.return_value.exists.return_value = True

        result = protocol_instance._has_frailty_device_observations(mock_patient)
        assert result is True


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_frailty_diagnoses_true(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_frailty_diagnoses returns True when frailty diagnosis exists."""
    mock_condition_objects.for_patient.return_value.find.return_value.committed.return_value.filter.return_value.filter.return_value.exists.return_value = True

    result = protocol_instance._has_frailty_diagnoses(mock_patient)
    assert result is True


@patch("canvas_sdk.v1.data.encounter.Encounter.objects")
def test_has_frailty_encounters_via_snomed(
    mock_encounter_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_frailty_encounters returns True when SNOMED encounter exists."""
    with patch.object(protocol_instance, "_get_value_set_codes", return_value={"123456"}):
        mock_encounter_objects.filter.return_value.exists.return_value = True

        result = protocol_instance._has_frailty_encounters(mock_patient)
        assert result is True


@patch("canvas_sdk.v1.data.claim_line_item.ClaimLineItem.objects")
@patch("canvas_sdk.v1.data.encounter.Encounter.objects")
@patch("cms131v14_diabetes_eye_exam.protocols.cms131v14_protocol.FrailtyEncounter")
def test_has_frailty_encounters_via_cpt_claim(
    mock_frailty_encounter: MagicMock,
    mock_encounter_objects: MagicMock,
    mock_claim_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_frailty_encounters returns True when CPT claim exists."""
    with patch.object(protocol_instance, "_get_value_set_codes", return_value=set()):
        mock_frailty_encounter.CPT = {"99304"}
        mock_frailty_encounter.HCPCSLEVELII = set()
        mock_encounter_objects.filter.return_value.exists.return_value = False
        mock_claim_objects.filter.return_value.exists.return_value = True

        result = protocol_instance._has_frailty_encounters(mock_patient)
        assert result is True


@patch("canvas_sdk.v1.data.claim_line_item.ClaimLineItem.objects")
@patch("canvas_sdk.v1.data.encounter.Encounter.objects")
@patch("cms131v14_diabetes_eye_exam.protocols.cms131v14_protocol.FrailtyEncounter")
def test_has_frailty_encounters_via_hcpcs_claim(
    mock_frailty_encounter: MagicMock,
    mock_encounter_objects: MagicMock,
    mock_claim_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_frailty_encounters returns True when HCPCS claim exists."""
    with patch.object(protocol_instance, "_get_value_set_codes", return_value=set()):
        mock_frailty_encounter.CPT = set()
        mock_frailty_encounter.HCPCSLEVELII = {"G0156"}
        mock_encounter_objects.filter.return_value.exists.return_value = False
        mock_claim_objects.filter.return_value.exists.return_value = True

        result = protocol_instance._has_frailty_encounters(mock_patient)
        assert result is True


@patch("canvas_sdk.v1.data.claim_line_item.ClaimLineItem.objects")
@patch("canvas_sdk.v1.data.encounter.Encounter.objects")
@patch("cms131v14_diabetes_eye_exam.protocols.cms131v14_protocol.FrailtyEncounter")
def test_has_frailty_encounters_no_cpt_hcpcs_attributes(
    mock_frailty_encounter: MagicMock,
    mock_encounter_objects: MagicMock,
    mock_claim_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_frailty_encounters handles case when CPT/HCPCS attributes don't exist."""
    with patch.object(protocol_instance, "_get_value_set_codes", return_value=set()):
        if hasattr(mock_frailty_encounter, "CPT"):
            delattr(mock_frailty_encounter, "CPT")
        if hasattr(mock_frailty_encounter, "HCPCSLEVELII"):
            delattr(mock_frailty_encounter, "HCPCSLEVELII")
        mock_encounter_objects.filter.return_value.exists.return_value = False

        result = protocol_instance._has_frailty_encounters(mock_patient)
        assert result is False


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_frailty_symptoms_true(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_frailty_symptoms returns True when frailty symptom exists."""
    mock_condition_objects.for_patient.return_value.find.return_value.committed.return_value.filter.return_value.filter.return_value.exists.return_value = True

    result = protocol_instance._has_frailty_symptoms(mock_patient)
    assert result is True


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_get_patient_with_condition_updated_event(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
    mock_condition: Mock,
) -> None:
    """Test _get_patient_and_condition returns patient and condition for CONDITION_UPDATED event."""
    protocol_instance.event.type = EventType.CONDITION_UPDATED
    mock_condition.patient = mock_patient
    mock_condition_objects.filter.return_value.select_related.return_value.first.return_value = (
        mock_condition
    )

    patient, condition = protocol_instance._get_patient_and_condition()
    assert patient == mock_patient
    assert condition == mock_condition


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_get_patient_with_condition_resolved_event(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
    mock_condition: Mock,
) -> None:
    """Test _get_patient_and_condition returns patient and condition for CONDITION_RESOLVED event."""
    protocol_instance.event.type = EventType.CONDITION_RESOLVED
    mock_condition.patient = mock_patient
    mock_condition_objects.filter.return_value.select_related.return_value.first.return_value = (
        mock_condition
    )

    patient, condition = protocol_instance._get_patient_and_condition()
    assert patient == mock_patient
    assert condition == mock_condition


@patch("canvas_sdk.v1.data.patient.Patient.objects")
def test_get_patient_from_event_context(
    mock_patient_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _get_patient_and_condition gets patient from event context."""
    protocol_instance.event.type = EventType.OBSERVATION_CREATED
    protocol_instance.event.context = {"patient": {"id": "patient-123"}}
    mock_patient_objects.filter.return_value.first.return_value = mock_patient

    patient, condition = protocol_instance._get_patient_and_condition()
    assert patient == mock_patient
    assert condition is None
    mock_patient_objects.filter.assert_called_once_with(id="patient-123")


@patch("canvas_sdk.v1.data.patient.Patient.objects")
@patch.object(CMS131v14DiabetesEyeExam, "patient_id_from_target")
def test_get_patient_from_patient_id_from_target_fallback(
    mock_patient_id_from_target: MagicMock,
    mock_patient_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _get_patient_and_condition uses patient_id_from_target as fallback."""
    protocol_instance.event.type = EventType.MEDICATION_LIST_ITEM_CREATED
    protocol_instance.event.context = {}
    mock_patient_id_from_target.return_value = "patient-123"
    mock_patient_objects.filter.return_value.first.return_value = mock_patient

    patient, condition = protocol_instance._get_patient_and_condition()
    assert patient == mock_patient
    assert condition is None
    mock_patient_id_from_target.assert_called_once()


@patch.object(CMS131v14DiabetesEyeExam, "patient_id_from_target")
def test_get_patient_handles_value_error_from_patient_id_from_target(
    mock_patient_id_from_target: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
) -> None:
    """Test _get_patient_and_condition handles ValueError from patient_id_from_target."""
    protocol_instance.event.type = EventType.OBSERVATION_CREATED
    protocol_instance.event.context = {}
    mock_patient_id_from_target.side_effect = ValueError("Event type not supported")

    patient, condition = protocol_instance._get_patient_and_condition()
    assert patient is None
    assert condition is None


@patch("canvas_sdk.v1.data.patient.Patient.objects")
@patch.object(CMS131v14DiabetesEyeExam, "patient_id_from_target")
def test_get_patient_no_patient_found_anywhere(
    mock_patient_id_from_target: MagicMock,
    mock_patient_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
) -> None:
    """Test _get_patient_and_condition returns None when patient not found in any path."""
    protocol_instance.event.type = EventType.OBSERVATION_CREATED
    protocol_instance.event.context = {}
    mock_patient_id_from_target.side_effect = ValueError("Event type not supported")
    mock_patient_objects.filter.return_value.first.return_value = None

    patient, condition = protocol_instance._get_patient_and_condition()
    assert patient is None
    assert condition is None


@patch("canvas_sdk.v1.data.patient.Patient.objects")
def test_get_patient_from_context_patient_not_found(
    mock_patient_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
) -> None:
    """Test _get_patient_and_condition when patient ID in context but patient not found."""
    protocol_instance.event.type = EventType.OBSERVATION_CREATED
    protocol_instance.event.context = {"patient": {"id": "patient-123"}}
    mock_patient_objects.filter.return_value.first.return_value = None

    patient, condition = protocol_instance._get_patient_and_condition()
    assert patient is None
    assert condition is None


@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_get_diabetes_diagnosis_codes_with_multiple_conditions_and_codings(
    mock_condition_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _get_diabetes_diagnosis_codes extracts codes from multiple conditions with multiple codings."""
    mock_condition1 = Mock()
    mock_coding1 = Mock()
    mock_coding1.code = "E119"
    mock_coding2 = Mock()
    mock_coding2.code = "E1121"
    mock_condition1.codings.all.return_value = [mock_coding1, mock_coding2]

    mock_condition2 = Mock()
    mock_coding3 = Mock()
    mock_coding3.code = "E1165"
    mock_condition2.codings.all.return_value = [mock_coding3]

    mock_condition_objects.for_patient.return_value.find.return_value.active.return_value.filter.return_value = [
        mock_condition1,
        mock_condition2,
    ]

    result = protocol_instance._get_diabetes_diagnosis_codes(mock_patient)
    assert "E119" in result
    assert "E1121" in result
    assert "E1165" in result
    assert len(result) == 3


@patch.object(CMS131v14DiabetesEyeExam, "_observation_exists")
def test_has_retinal_finding_no_severity_in_prior_year_both_eyes(
    mock_observation_exists: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_retinal_finding_no_severity_in_prior_year returns True when both eyes have no retinopathy."""
    mock_observation_exists.side_effect = [True, True]

    result = protocol_instance._has_retinal_finding_no_severity_in_prior_year(mock_patient)
    assert result is True
    assert mock_observation_exists.call_count == 2


@patch("canvas_sdk.effects.protocol_card.protocol_card.ProtocolCard.apply")
def test_create_not_applicable_card(
    mock_apply: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _create_not_applicable_card creates card with NOT_APPLICABLE status."""
    mock_apply.return_value = "NOT_APPLICABLE_EFFECT"

    effect = protocol_instance._create_not_applicable_card(mock_patient)
    assert effect == "NOT_APPLICABLE_EFFECT"
    mock_apply.assert_called_once()


@patch.object(CMS131v14DiabetesEyeExam, "_observation_exists")
def test_has_retinal_finding_with_severity_both_eyes(
    mock_observation_exists: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_retinal_finding_with_severity returns True when both eyes have retinopathy."""
    mock_observation_exists.side_effect = [True, True, False, False]

    result = protocol_instance._has_retinal_finding_with_severity_in_period(mock_patient)
    assert result is True


@patch("canvas_sdk.v1.data.referral.ReferralReport.objects")
def test_referral_report_exists_with_specialty_fallback(
    mock_referral_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _referral_report_exists uses specialty fallback when no codings match."""
    mock_referral_objects.filter.return_value.exists.return_value = False
    mock_referral_specialty = Mock()
    mock_referral_specialty.exists.return_value = True
    mock_referral_objects.filter.return_value.filter.return_value = mock_referral_specialty

    result = protocol_instance._referral_report_exists(
        mock_patient,
        arrow.get("2024-01-01").datetime,
        arrow.get("2024-12-31").datetime,
    )
    assert result is True


@patch.object(CMS131v14DiabetesEyeExam, "_referral_report_exists")
def test_has_retinal_exam_in_period_true(
    mock_referral_exists: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_retinal_exam_in_period returns True when referral report exists."""
    mock_referral_exists.return_value = True

    result = protocol_instance._has_retinal_exam_in_period(mock_patient)
    assert result is True
    mock_referral_exists.assert_called_once()


@patch.object(CMS131v14DiabetesEyeExam, "_referral_report_exists")
def test_has_retinal_exam_in_period_or_year_prior_true(
    mock_referral_exists: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_retinal_exam_in_period_or_year_prior returns True when referral report exists."""
    mock_referral_exists.return_value = True

    result = protocol_instance._has_retinal_exam_in_period_or_year_prior(mock_patient)
    assert result is True
    mock_referral_exists.assert_called_once()


@patch.object(CMS131v14DiabetesEyeExam, "_observation_exists")
@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_palliative_care_in_period_via_assessment(
    mock_condition_objects: MagicMock,
    mock_observation_exists: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_palliative_care_in_period returns True for palliative care assessment."""
    mock_condition_objects.for_patient.return_value.find.return_value.active.return_value.filter.return_value.exists.return_value = False
    mock_observation_exists.return_value = True

    result = protocol_instance._has_palliative_care_in_period(mock_patient)
    assert result is True


@patch("canvas_sdk.v1.data.encounter.Encounter.objects")
@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_palliative_care_in_period_via_encounter(
    mock_condition_objects: MagicMock,
    mock_encounter_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_palliative_care_in_period returns True for palliative care encounter."""
    mock_condition_objects.for_patient.return_value.find.return_value.active.return_value.filter.return_value.exists.return_value = False
    with (
        patch.object(protocol_instance, "_observation_exists", return_value=False),
        patch.object(protocol_instance, "_get_value_set_codes", return_value={"123456"}),
    ):
        mock_encounter_objects.filter.return_value.exists.return_value = True

        result = protocol_instance._has_palliative_care_in_period(mock_patient)
        assert result is True


@patch("canvas_sdk.v1.data.claim_line_item.ClaimLineItem.objects")
@patch("canvas_sdk.v1.data.encounter.Encounter.objects")
@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_palliative_care_in_period_via_claim(
    mock_condition_objects: MagicMock,
    mock_encounter_objects: MagicMock,
    mock_claim_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_palliative_care_in_period returns True for palliative care claim."""
    mock_condition_objects.for_patient.return_value.find.return_value.active.return_value.filter.return_value.exists.return_value = False
    with (
        patch.object(protocol_instance, "_observation_exists", return_value=False),
        patch.object(protocol_instance, "_get_value_set_codes", return_value=set()),
    ):
        mock_encounter_objects.filter.return_value.exists.return_value = False
        mock_claim = Mock()
        mock_claim.proc_code = "M1141"
        mock_claim_objects.filter.return_value.first.return_value = mock_claim

        result = protocol_instance._has_palliative_care_in_period(mock_patient)
        assert result is True


@patch("canvas_sdk.v1.data.medication.Medication.objects")
@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_advanced_illness_or_dementia_meds_dementia_meds(
    mock_condition_objects: MagicMock,
    mock_medication_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_advanced_illness_or_dementia_meds returns True for dementia meds."""
    mock_condition_objects.for_patient.return_value.find.return_value.filter.return_value.filter.return_value.exists.return_value = False
    mock_medication_objects.for_patient.return_value.committed.return_value.find.return_value.filter.return_value.exists.return_value = True

    result = protocol_instance._has_advanced_illness_or_dementia_meds(mock_patient)
    assert result is True


@patch("canvas_sdk.v1.data.medication.Medication.objects")
@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_advanced_illness_or_dementia_meds_exception(
    mock_condition_objects: MagicMock,
    mock_medication_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_advanced_illness_or_dementia_meds handles exceptions."""
    mock_condition_objects.for_patient.side_effect = Exception("Test exception")

    result = protocol_instance._has_advanced_illness_or_dementia_meds(mock_patient)
    assert result is False


@patch("canvas_sdk.v1.data.observation.Observation.objects")
@patch("canvas_sdk.v1.data.encounter.Encounter.objects")
@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_hospice_care_in_period_via_assessment(
    mock_condition_objects: MagicMock,
    mock_encounter_objects: MagicMock,
    mock_observation_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_hospice_care_in_period returns True for hospice care assessment."""
    mock_condition_objects.for_patient.return_value.find.return_value.active.return_value.filter.return_value.exists.return_value = False
    mock_encounter_objects.filter.return_value.exists.return_value = False
    mock_observation_objects.for_patient.return_value.filter.return_value.exists.side_effect = [
        False,
        True,
    ]

    result = protocol_instance._has_hospice_care_in_period(mock_patient)
    assert result is True


@patch("canvas_sdk.v1.data.claim_line_item.ClaimLineItem.objects")
@patch("canvas_sdk.v1.data.observation.Observation.objects")
@patch("canvas_sdk.v1.data.encounter.Encounter.objects")
@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_hospice_care_in_period_exception(
    mock_condition_objects: MagicMock,
    mock_encounter_objects: MagicMock,
    mock_observation_objects: MagicMock,
    mock_claim_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_hospice_care_in_period handles exceptions."""
    mock_condition_objects.for_patient.side_effect = Exception("Test exception")

    result = protocol_instance._has_hospice_care_in_period(mock_patient)
    assert result is False


@patch("canvas_sdk.v1.data.encounter.Encounter.objects")
@patch("canvas_sdk.v1.data.condition.Condition.objects")
def test_has_hospice_care_in_period_via_encounter(
    mock_condition_objects: MagicMock,
    mock_encounter_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_hospice_care_in_period returns True for hospice encounter."""
    mock_condition_objects.for_patient.return_value.find.return_value.active.return_value.filter.return_value.exists.return_value = False
    with patch.object(protocol_instance, "_get_value_set_codes", return_value={"123456"}):
        mock_encounter_objects.filter.return_value.exists.return_value = True

        result = protocol_instance._has_hospice_care_in_period(mock_patient)
        assert result is True


@patch("canvas_sdk.v1.data.claim_line_item.ClaimLineItem.objects")
@patch("canvas_sdk.v1.data.encounter.Encounter.objects")
def test_has_eligible_encounter_in_period_via_claim(
    mock_encounter_objects: MagicMock,
    mock_claim_objects: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
) -> None:
    """Test _has_eligible_encounter_in_period returns True when eligible claim exists."""
    mock_encounter_objects.filter.return_value.first.return_value = None
    mock_claim = Mock()
    mock_claim.proc_code = "99385"
    mock_claim_objects.filter.return_value.first.return_value = mock_claim

    result = protocol_instance._has_eligible_encounter_in_period(mock_patient)
    assert result is True


@patch.object(CMS131v14DiabetesEyeExam, "_create_due_card")
@patch.object(CMS131v14DiabetesEyeExam, "_create_satisfied_card")
@patch.object(CMS131v14DiabetesEyeExam, "_in_numerator")
@patch.object(CMS131v14DiabetesEyeExam, "_in_denominator")
@patch.object(CMS131v14DiabetesEyeExam, "_in_initial_population")
@patch.object(CMS131v14DiabetesEyeExam, "_should_remove_card")
@patch.object(CMS131v14DiabetesEyeExam, "_get_patient_and_condition")
def test_compute_creates_satisfied_card(
    mock_get_patient: MagicMock,
    mock_should_remove: MagicMock,
    mock_in_initial: MagicMock,
    mock_in_denominator: MagicMock,
    mock_in_numerator: MagicMock,
    mock_create_satisfied: MagicMock,
    mock_create_due: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
    mock_condition: Mock,
) -> None:
    """Test compute returns SATISFIED card when patient is in numerator."""
    mock_get_patient.return_value = (mock_patient, mock_condition)
    mock_should_remove.return_value = False
    mock_in_initial.return_value = True
    mock_in_denominator.return_value = True
    mock_in_numerator.return_value = True
    mock_create_satisfied.return_value = "SATISFIED_CARD"

    effects = protocol_instance.compute()
    assert effects == ["SATISFIED_CARD"]
    mock_create_satisfied.assert_called_once_with(mock_patient)
    mock_create_due.assert_not_called()


@patch.object(CMS131v14DiabetesEyeExam, "_create_due_card")
@patch.object(CMS131v14DiabetesEyeExam, "_create_satisfied_card")
@patch.object(CMS131v14DiabetesEyeExam, "_in_numerator")
@patch.object(CMS131v14DiabetesEyeExam, "_in_denominator")
@patch.object(CMS131v14DiabetesEyeExam, "_in_initial_population")
@patch.object(CMS131v14DiabetesEyeExam, "_should_remove_card")
@patch.object(CMS131v14DiabetesEyeExam, "_get_patient_and_condition")
def test_compute_creates_due_card(
    mock_get_patient: MagicMock,
    mock_should_remove: MagicMock,
    mock_in_initial: MagicMock,
    mock_in_denominator: MagicMock,
    mock_in_numerator: MagicMock,
    mock_create_satisfied: MagicMock,
    mock_create_due: MagicMock,
    protocol_instance: CMS131v14DiabetesEyeExam,
    mock_patient: Mock,
    mock_condition: Mock,
) -> None:
    """Test compute returns DUE card when patient is not in numerator."""
    mock_get_patient.return_value = (mock_patient, mock_condition)
    mock_should_remove.return_value = False
    mock_in_initial.return_value = True
    mock_in_denominator.return_value = True
    mock_in_numerator.return_value = False
    mock_create_due.return_value = "DUE_CARD"

    effects = protocol_instance.compute()
    assert effects == ["DUE_CARD"]
    mock_create_due.assert_called_once_with(mock_patient)
    mock_create_satisfied.assert_not_called()
