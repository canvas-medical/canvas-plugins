import json
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.patient_group import PatientGroupEffect

MOCK_PATIENT = "canvas_sdk.effects.patient_group.Patient.objects"
MOCK_GROUP = "canvas_sdk.effects.patient_group.PatientGroupModel.objects"


def _mock_group_exists(mock: MagicMock, exists: bool = True) -> None:
    mock.filter.return_value.exists.return_value = exists


def _mock_patients_exist(mock: MagicMock, patient_ids: list[str]) -> None:
    mock.filter.return_value.values_list.return_value = patient_ids


@pytest.mark.parametrize(
    "method,expected_type",
    [
        ("add_member", EffectType.PATIENT_GROUP__ADD_MEMBER),
        ("deactivate_member", EffectType.PATIENT_GROUP__DEACTIVATE_MEMBER),
    ],
)
@patch(MOCK_GROUP)
@patch(MOCK_PATIENT)
def test_effect_type(
    mock_patient: MagicMock, mock_group: MagicMock, method: str, expected_type: EffectType
) -> None:
    """Test that each method returns the correct effect type."""
    _mock_patients_exist(mock_patient, ["patient-1"])
    _mock_group_exists(mock_group)
    group = PatientGroupEffect(group_id="group-1")
    applied = getattr(group, method)(patient_ids=["patient-1"])
    assert applied.type == expected_type


@pytest.mark.parametrize("method", ["add_member", "deactivate_member"])
@patch(MOCK_GROUP)
@patch(MOCK_PATIENT)
def test_single_patient_payload(
    mock_patient: MagicMock, mock_group: MagicMock, method: str
) -> None:
    """Test payload with a single patient."""
    _mock_patients_exist(mock_patient, ["patient-uuid"])
    _mock_group_exists(mock_group)
    group = PatientGroupEffect(group_id="group-uuid")
    applied = getattr(group, method)(patient_ids=["patient-uuid"])
    payload = json.loads(applied.payload)

    assert payload == {"data": {"patient_ids": ["patient-uuid"], "group_id": "group-uuid"}}


@pytest.mark.parametrize("method", ["add_member", "deactivate_member"])
@patch(MOCK_GROUP)
@patch(MOCK_PATIENT)
def test_multiple_patients_payload(
    mock_patient: MagicMock, mock_group: MagicMock, method: str
) -> None:
    """Test payload with multiple patients."""
    _mock_patients_exist(mock_patient, ["patient-1", "patient-2"])
    _mock_group_exists(mock_group)
    group = PatientGroupEffect(group_id="group-uuid")
    applied = getattr(group, method)(patient_ids=["patient-1", "patient-2"])
    payload = json.loads(applied.payload)

    assert payload["data"]["patient_ids"] == ["patient-1", "patient-2"]
    assert payload["data"]["group_id"] == "group-uuid"


@pytest.mark.parametrize("method", ["add_member", "deactivate_member"])
@patch(MOCK_GROUP)
def test_empty_patients_payload(mock_group: MagicMock, method: str) -> None:
    """Test payload with an empty patient list."""
    _mock_group_exists(mock_group)
    group = PatientGroupEffect(group_id="group-uuid")
    applied = getattr(group, method)(patient_ids=[])
    payload = json.loads(applied.payload)

    assert payload["data"]["patient_ids"] == []
    assert payload["data"]["group_id"] == "group-uuid"


@pytest.mark.parametrize("method", ["add_member", "deactivate_member"])
@patch(MOCK_GROUP)
@patch(MOCK_PATIENT)
def test_invalid_patient_raises(
    mock_patient: MagicMock, mock_group: MagicMock, method: str
) -> None:
    """Test that a nonexistent patient raises ValidationError."""
    _mock_patients_exist(mock_patient, [])
    _mock_group_exists(mock_group)
    group = PatientGroupEffect(group_id="group-1")
    with pytest.raises(ValidationError, match="Patient with id.*does not exist"):
        getattr(group, method)(patient_ids=["nonexistent-patient"])


@pytest.mark.parametrize("method", ["add_member", "deactivate_member"])
@patch(MOCK_GROUP)
def test_invalid_group_raises(mock_group: MagicMock, method: str) -> None:
    """Test that a nonexistent group raises ValidationError."""
    _mock_group_exists(mock_group, exists=False)
    group = PatientGroupEffect(group_id="nonexistent-group")
    with pytest.raises(ValidationError, match="PatientGroup with id.*does not exist"):
        getattr(group, method)(patient_ids=[])
