"""Tests for RemoveDocumentFromPatient effect."""

import json

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.data_integration import RemoveDocumentFromPatient


def test_create_effect_with_document_id_only() -> None:
    """Test creating effect with just document_id succeeds."""
    effect = RemoveDocumentFromPatient(document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890")
    applied = effect.apply()

    assert applied.type == EffectType.REMOVE_DOCUMENT_FROM_PATIENT

    payload = json.loads(applied.payload)
    assert payload["data"] == {
        "document_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "patient_id": None,
    }


def test_create_effect_with_patient_id() -> None:
    """Test creating effect with document_id and patient_id succeeds."""
    effect = RemoveDocumentFromPatient(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        patient_id="abc123",
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"] == {
        "document_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "patient_id": "abc123",
    }


def test_values_property_returns_correct_structure() -> None:
    """Test values property returns correctly structured dict."""
    effect = RemoveDocumentFromPatient(document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890")

    assert effect.values == {
        "document_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "patient_id": None,
    }


def test_meta_effect_type() -> None:
    """Test that Meta.effect_type is correct."""
    assert RemoveDocumentFromPatient.Meta.effect_type == EffectType.REMOVE_DOCUMENT_FROM_PATIENT


def test_effect_payload_uses_data_wrapper() -> None:
    """Test that effect_payload uses the base class data wrapper."""
    effect = RemoveDocumentFromPatient(document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890")
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert "data" in payload
    assert payload["data"]["document_id"] == "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
