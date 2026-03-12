import json

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.patient_group import PatientGroupAddMember, PatientGroupDeactivateMember


def test_add_member_effect_type() -> None:
    """Test that PatientGroupAddMember has the correct effect type."""
    effect = PatientGroupAddMember(
        patient_ids=["patient-1"],
        group_id="group-1",
    )
    applied = effect.apply()
    assert applied.type == EffectType.PATIENT_GROUP__ADD_MEMBER


def test_add_member_single_patient_payload() -> None:
    """Test PatientGroupAddMember payload with a single patient."""
    effect = PatientGroupAddMember(
        patient_ids=["patient-uuid"],
        group_id="group-uuid",
    )
    applied = effect.apply()
    payload = json.loads(applied.payload)

    assert payload == {"patient_ids": ["patient-uuid"], "group_id": "group-uuid"}


def test_add_member_multiple_patients_payload() -> None:
    """Test PatientGroupAddMember payload with multiple patients."""
    effect = PatientGroupAddMember(
        patient_ids=["patient-1", "patient-2", "patient-3"],
        group_id="group-uuid",
    )
    applied = effect.apply()
    payload = json.loads(applied.payload)

    assert payload["patient_ids"] == ["patient-1", "patient-2", "patient-3"]
    assert payload["group_id"] == "group-uuid"


def test_add_member_empty_patients_payload() -> None:
    """Test PatientGroupAddMember payload with empty patient list."""
    effect = PatientGroupAddMember(
        patient_ids=[],
        group_id="group-uuid",
    )
    applied = effect.apply()
    payload = json.loads(applied.payload)

    assert payload["patient_ids"] == []
    assert payload["group_id"] == "group-uuid"


def test_add_member_missing_group_id_raises() -> None:
    """Test that apply raises when group_id is not set."""
    effect = PatientGroupAddMember(patient_ids=["patient-1"])
    with pytest.raises(ValidationError):
        effect.apply()


def test_add_member_default_patient_ids_is_empty_list() -> None:
    """Test that patient_ids defaults to an empty list and apply succeeds."""
    effect = PatientGroupAddMember(group_id="group-1")
    applied = effect.apply()
    payload = json.loads(applied.payload)

    assert payload["patient_ids"] == []
    assert payload["group_id"] == "group-1"


def test_deactivate_member_effect_type() -> None:
    """Test that PatientGroupDeactivateMember has the correct effect type."""
    effect = PatientGroupDeactivateMember(
        patient_ids=["patient-1"],
        group_id="group-1",
    )
    applied = effect.apply()
    assert applied.type == EffectType.PATIENT_GROUP__DEACTIVATE_MEMBER


def test_deactivate_member_single_patient_payload() -> None:
    """Test PatientGroupDeactivateMember payload with a single patient."""
    effect = PatientGroupDeactivateMember(
        patient_ids=["patient-uuid"],
        group_id="group-uuid",
    )
    applied = effect.apply()
    payload = json.loads(applied.payload)

    assert payload == {"patient_ids": ["patient-uuid"], "group_id": "group-uuid"}


def test_deactivate_member_multiple_patients_payload() -> None:
    """Test PatientGroupDeactivateMember payload with multiple patients."""
    effect = PatientGroupDeactivateMember(
        patient_ids=["patient-1", "patient-2"],
        group_id="group-uuid",
    )
    applied = effect.apply()
    payload = json.loads(applied.payload)

    assert payload["patient_ids"] == ["patient-1", "patient-2"]
    assert payload["group_id"] == "group-uuid"


def test_deactivate_member_missing_group_id_raises() -> None:
    """Test that apply raises when group_id is not set."""
    effect = PatientGroupDeactivateMember(patient_ids=["patient-1"])
    with pytest.raises(ValidationError):
        effect.apply()


def test_deactivate_member_default_patient_ids_is_empty_list() -> None:
    """Test that patient_ids defaults to an empty list and apply succeeds."""
    effect = PatientGroupDeactivateMember(group_id="group-1")
    applied = effect.apply()
    payload = json.loads(applied.payload)

    assert payload["patient_ids"] == []
    assert payload["group_id"] == "group-1"


def test_add_member_values_is_empty() -> None:
    """Test that the values property returns an empty dict."""
    effect = PatientGroupAddMember(patient_ids=["p1"], group_id="g1")
    assert effect.values == {}


def test_deactivate_member_values_is_empty() -> None:
    """Test that the values property returns an empty dict."""
    effect = PatientGroupDeactivateMember(patient_ids=["p1"], group_id="g1")
    assert effect.values == {}
