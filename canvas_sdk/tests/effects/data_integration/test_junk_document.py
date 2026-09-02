"""Tests for JunkDocument effect."""

import json

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.data_integration import JunkDocument


def test_create_effect_with_document_id() -> None:
    """Test creating effect with just document_id succeeds."""
    effect = JunkDocument(document_id="12345")
    applied = effect.apply()

    assert applied.type == EffectType.JUNK_DOCUMENT

    payload = json.loads(applied.payload)
    assert payload["data"]["document_id"] == "12345"


def test_create_effect_with_integer_document_id() -> None:
    """Test creating effect with integer document_id serializes as string."""
    effect = JunkDocument(document_id=42)
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["document_id"] == "42"


def test_values_property_returns_correct_structure() -> None:
    """Test values property returns correctly structured dict."""
    effect = JunkDocument(document_id="12345")

    values = effect.values

    assert values == {"document_id": "12345"}


def test_values_strips_whitespace_from_document_id() -> None:
    """Test values property strips whitespace from document_id."""
    effect = JunkDocument(document_id="  12345  ")

    values = effect.values

    assert values == {"document_id": "12345"}


def test_apply_raises_error_when_document_id_missing() -> None:
    """Test apply raises error when document_id is missing."""
    effect = JunkDocument()
    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    assert "document_id" in str(exc_info.value)


def test_apply_raises_error_when_document_id_is_empty() -> None:
    """Test apply raises error when document_id is empty string."""
    effect = JunkDocument(document_id="")
    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    assert "document_id must be a non-empty string" in str(exc_info.value)


def test_apply_raises_error_when_document_id_is_whitespace() -> None:
    """Test apply raises error when document_id is only whitespace."""
    effect = JunkDocument(document_id="   ")
    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    assert "document_id must be a non-empty string" in str(exc_info.value)


def test_meta_effect_type() -> None:
    """Test that Meta.effect_type is correct."""
    assert JunkDocument.Meta.effect_type == EffectType.JUNK_DOCUMENT


def test_meta_apply_required_fields() -> None:
    """Test that Meta.apply_required_fields includes document_id."""
    assert "document_id" in JunkDocument.Meta.apply_required_fields


def test_effect_payload_uses_data_wrapper() -> None:
    """Test that effect_payload uses the base class data wrapper."""
    effect = JunkDocument(document_id="12345")
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert "data" in payload
    assert payload["data"]["document_id"] == "12345"
