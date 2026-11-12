"""Tests for RemoveDocumentFromPatient effect."""

import json

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.data_integration import RemoveDocumentFromPatient


def test_create_effect_with_document_id_only() -> None:
    """Test creating effect with just document_id succeeds."""
    effect = RemoveDocumentFromPatient(document_id="12345")
    applied = effect.apply()

    assert applied.type == EffectType.REMOVE_DOCUMENT_FROM_PATIENT

    payload = json.loads(applied.payload)
    assert payload["data"]["document_id"] == "12345"
    assert "patient_id" not in payload["data"]


def test_create_effect_with_integer_document_id() -> None:
    """Test creating effect with integer document_id succeeds."""
    effect = RemoveDocumentFromPatient(document_id=42)
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["document_id"] == "42"


def test_create_effect_with_patient_id() -> None:
    """Test creating effect with document_id and patient_id succeeds."""
    effect = RemoveDocumentFromPatient(
        document_id="12345",
        patient_id="abc123",
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["document_id"] == "12345"
    assert payload["data"]["patient_id"] == "abc123"


def test_values_property_returns_correct_structure() -> None:
    """Test values property returns correctly structured dict."""
    effect = RemoveDocumentFromPatient(document_id="12345")

    values = effect.values

    assert values == {"document_id": "12345"}


def test_values_property_with_patient_id() -> None:
    """Test values property includes patient_id when provided."""
    effect = RemoveDocumentFromPatient(
        document_id="12345",
        patient_id="patient123",
    )

    values = effect.values

    assert values == {
        "document_id": "12345",
        "patient_id": "patient123",
    }


def test_values_property_excludes_none_patient_id() -> None:
    """Test values property excludes patient_id when None."""
    effect = RemoveDocumentFromPatient(
        document_id="12345",
        patient_id=None,
    )

    values = effect.values

    assert "patient_id" not in values


def test_apply_raises_error_when_document_id_missing() -> None:
    """Test apply raises error when document_id is missing."""
    effect = RemoveDocumentFromPatient()
    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    assert "document_id" in str(exc_info.value)


def test_apply_raises_error_when_document_id_is_empty() -> None:
    """Test apply raises error when document_id is empty string."""
    effect = RemoveDocumentFromPatient(document_id="")
    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    assert "document_id must be a non-empty string" in str(exc_info.value)


def test_apply_raises_error_when_document_id_is_whitespace() -> None:
    """Test apply raises error when document_id is only whitespace."""
    effect = RemoveDocumentFromPatient(document_id="   ")
    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    assert "document_id must be a non-empty string" in str(exc_info.value)


def test_apply_raises_error_when_patient_id_is_empty() -> None:
    """Test apply raises error when patient_id is empty string."""
    effect = RemoveDocumentFromPatient(
        document_id="12345",
        patient_id="",
    )
    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    assert "patient_id must be a non-empty string" in str(exc_info.value)


def test_apply_raises_error_when_patient_id_is_whitespace() -> None:
    """Test apply raises error when patient_id is only whitespace."""
    effect = RemoveDocumentFromPatient(
        document_id="12345",
        patient_id="   ",
    )
    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    assert "patient_id must be a non-empty string" in str(exc_info.value)


def test_values_strips_whitespace_from_document_id() -> None:
    """Test values property strips whitespace from document_id."""
    effect = RemoveDocumentFromPatient(document_id=" 12345 ")
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["document_id"] == "12345"


def test_values_strips_whitespace_from_patient_id() -> None:
    """Test values property strips whitespace from patient_id."""
    effect = RemoveDocumentFromPatient(
        document_id="12345",
        patient_id="  abc123  ",
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["patient_id"] == "abc123"


def test_meta_effect_type() -> None:
    """Test that Meta.effect_type is correct."""
    assert RemoveDocumentFromPatient.Meta.effect_type == EffectType.REMOVE_DOCUMENT_FROM_PATIENT


def test_meta_apply_required_fields() -> None:
    """Test that Meta.apply_required_fields includes document_id."""
    assert "document_id" in RemoveDocumentFromPatient.Meta.apply_required_fields


def test_effect_payload_uses_data_wrapper() -> None:
    """Test that effect_payload uses the base class data wrapper."""
    effect = RemoveDocumentFromPatient(document_id="12345")
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert "data" in payload
    assert payload["data"]["document_id"] == "12345"


def test_apply_with_all_fields() -> None:
    """Test apply with all fields populated."""
    effect = RemoveDocumentFromPatient(
        document_id="12345",
        patient_id="patient123",
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["document_id"] == "12345"
    assert payload["data"]["patient_id"] == "patient123"
