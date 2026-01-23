"""Tests for RemoveDocumentFromPatient effect."""

import json

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.data_integration import (
    RemoveDocumentConfidenceScores,
    RemoveDocumentFromPatient,
)
from canvas_sdk.effects.data_integration.remove_document_from_patient import CONFIDENCE_SCORE_KEYS


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


def test_create_effect_with_confidence_scores() -> None:
    """Test creating effect with confidence_scores succeeds."""
    effect = RemoveDocumentFromPatient(
        document_id="12345",
        confidence_scores={"removal": 0.95},
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["confidence_scores"] == {"removal": 0.95}


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


def test_values_property_with_confidence_scores() -> None:
    """Test values property includes confidence_scores when provided."""
    effect = RemoveDocumentFromPatient(
        document_id="12345",
        confidence_scores={"removal": 0.9},
    )

    values = effect.values

    assert "confidence_scores" in values
    assert values["confidence_scores"] == {"removal": 0.9}


def test_values_property_excludes_none_confidence_scores() -> None:
    """Test values property excludes confidence_scores when None."""
    effect = RemoveDocumentFromPatient(document_id="12345")

    values = effect.values

    assert "confidence_scores" not in values


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


def test_creation_raises_error_for_invalid_confidence_scores_key() -> None:
    """Test creation raises error for invalid keys in confidence_scores.

    The model_validator catches invalid keys before Pydantic processes
    the TypedDict (which would otherwise silently drop unknown keys).
    """
    with pytest.raises(ValidationError) as exc_info:
        RemoveDocumentFromPatient(
            document_id="12345",
            confidence_scores={
                "removal": 0.9,
                "invalid_key": 0.5,  # type: ignore[typeddict-unknown-key]
            },
        )

    err_msg = str(exc_info.value)
    assert "invalid keys" in err_msg
    assert "invalid_key" in err_msg


def test_creation_raises_error_when_confidence_score_below_zero() -> None:
    """Test creation raises error when confidence score is below 0.

    Pydantic validates the range constraint at construction time via
    the Annotated[float, Field(ge=0.0, le=1.0)] type annotation.
    """
    with pytest.raises(ValidationError) as exc_info:
        RemoveDocumentFromPatient(
            document_id="12345",
            confidence_scores={"removal": -0.1},
        )

    err_msg = str(exc_info.value)
    assert "greater_than_equal" in err_msg or "greater than or equal to 0" in err_msg


def test_creation_raises_error_when_confidence_score_above_one() -> None:
    """Test creation raises error when confidence score is above 1.0.

    Pydantic validates the range constraint at construction time via
    the Annotated[float, Field(ge=0.0, le=1.0)] type annotation.
    """
    with pytest.raises(ValidationError) as exc_info:
        RemoveDocumentFromPatient(
            document_id="12345",
            confidence_scores={"removal": 1.5},
        )

    err_msg = str(exc_info.value)
    assert "less_than_equal" in err_msg or "less than or equal to 1" in err_msg


def test_creation_raises_error_when_confidence_score_is_not_numeric() -> None:
    """Test creation raises error when confidence score is not a number.

    Pydantic validates types at construction time.
    """
    with pytest.raises(ValidationError) as exc_info:
        RemoveDocumentFromPatient(
            document_id="12345",
            confidence_scores={"removal": "high"},  # type: ignore[typeddict-item]
        )

    err_msg = str(exc_info.value)
    assert "float_type" in err_msg or "valid number" in err_msg


def test_apply_succeeds_with_boundary_confidence_scores() -> None:
    """Test apply succeeds with boundary values 0.0 and 1.0."""
    effect = RemoveDocumentFromPatient(
        document_id="12345",
        confidence_scores={"removal": 0.0},
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["confidence_scores"]["removal"] == 0.0

    effect2 = RemoveDocumentFromPatient(
        document_id="12345",
        confidence_scores={"removal": 1.0},
    )
    applied2 = effect2.apply()

    payload2 = json.loads(applied2.payload)
    assert payload2["data"]["confidence_scores"]["removal"] == 1.0


def test_apply_accepts_integer_confidence_scores() -> None:
    """Test apply accepts integer values for confidence scores."""
    effect = RemoveDocumentFromPatient(
        document_id="12345",
        confidence_scores={"removal": 1},
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["confidence_scores"]["removal"] == 1


def test_apply_with_all_fields() -> None:
    """Test apply with all fields populated."""
    effect = RemoveDocumentFromPatient(
        document_id="12345",
        patient_id="patient123",
        confidence_scores={"removal": 0.87},
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["document_id"] == "12345"
    assert payload["data"]["patient_id"] == "patient123"
    assert payload["data"]["confidence_scores"]["removal"] == 0.87


def test_confidence_score_keys_are_correct() -> None:
    """Test CONFIDENCE_SCORE_KEYS contains expected keys."""
    expected = {"removal"}
    assert expected == CONFIDENCE_SCORE_KEYS


def test_confidence_score_keys_is_frozen() -> None:
    """Test CONFIDENCE_SCORE_KEYS is immutable."""
    assert isinstance(CONFIDENCE_SCORE_KEYS, frozenset)


def test_confidence_score_keys_derived_from_typeddict() -> None:
    """Test CONFIDENCE_SCORE_KEYS matches RemoveDocumentConfidenceScores TypedDict annotations."""
    assert frozenset(RemoveDocumentConfidenceScores.__annotations__.keys()) == CONFIDENCE_SCORE_KEYS


def test_confidence_scores_accepts_valid_typed_dict() -> None:
    """Test that RemoveDocumentConfidenceScores TypedDict works with valid values."""
    scores: RemoveDocumentConfidenceScores = {"removal": 0.95}
    effect = RemoveDocumentFromPatient(
        document_id="12345",
        confidence_scores=scores,
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["confidence_scores"]["removal"] == 0.95


def test_confidence_scores_typeddict_has_expected_keys() -> None:
    """Test RemoveDocumentConfidenceScores TypedDict defines expected keys."""
    expected_keys = {"removal"}
    assert set(RemoveDocumentConfidenceScores.__annotations__.keys()) == expected_keys


def test_confidence_scores_typeddict_is_total_false() -> None:
    """Test RemoveDocumentConfidenceScores TypedDict has total=False (all keys optional)."""
    assert not RemoveDocumentConfidenceScores.__required_keys__
