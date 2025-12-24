import json

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.data_integration import RemoveDocumentFromPatientEffect


class TestRemoveDocumentFromPatientEffect:
    """Tests for the RemoveDocumentFromPatientEffect class."""

    def test_effect_creation_with_document_id_only(self) -> None:
        """Test that an effect can be created with just document_id."""
        effect = RemoveDocumentFromPatientEffect(document_id="123")
        assert effect.document_id == "123"
        assert effect.patient_id is None
        assert effect.confidence_scores is None

    def test_effect_creation_with_patient_id(self) -> None:
        """Test that an effect can be created with document_id and patient_id."""
        effect = RemoveDocumentFromPatientEffect(document_id="123", patient_id="abc123")
        assert effect.document_id == "123"
        assert effect.patient_id == "abc123"

    def test_effect_creation_with_confidence_scores(self) -> None:
        """Test that an effect can be created with document_id and confidence_scores."""
        effect = RemoveDocumentFromPatientEffect(document_id="123", confidence_scores={"123": 0.95})
        assert effect.document_id == "123"
        assert effect.confidence_scores == {"123": 0.95}

    def test_values_property_without_confidence_scores(self) -> None:
        """Test that values property returns correct dict without confidence_scores."""
        effect = RemoveDocumentFromPatientEffect(document_id="456")
        assert effect.values == {"document_id": "456"}

    def test_values_property_with_patient_id(self) -> None:
        """Test that values property includes patient_id when present."""
        effect = RemoveDocumentFromPatientEffect(document_id="456", patient_id="patient123")
        assert effect.values == {"document_id": "456", "patient_id": "patient123"}

    def test_values_property_with_confidence_scores(self) -> None:
        """Test that values property returns correct dict with confidence_scores."""
        effect = RemoveDocumentFromPatientEffect(document_id="789", confidence_scores={"789": 0.85})
        assert effect.values == {"document_id": "789", "confidence_scores": {"789": 0.85}}

    def test_effect_payload(self) -> None:
        """Test that effect_payload returns values directly (no data wrapper)."""
        effect = RemoveDocumentFromPatientEffect(document_id="100")
        assert effect.effect_payload == {"document_id": "100"}

    def test_effect_payload_with_confidence_scores(self) -> None:
        """Test that effect_payload includes confidence_scores when present."""
        effect = RemoveDocumentFromPatientEffect(document_id="100", confidence_scores={"100": 0.75})
        expected = {"document_id": "100", "confidence_scores": {"100": 0.75}}
        assert effect.effect_payload == expected

    def test_effect_payload_with_patient_id(self) -> None:
        """Test that effect_payload includes patient_id when present."""
        effect = RemoveDocumentFromPatientEffect(document_id="100", patient_id="patient456")
        expected = {"document_id": "100", "patient_id": "patient456"}
        assert effect.effect_payload == expected

    def test_apply_returns_correct_effect_type(self) -> None:
        """Test that apply() returns an Effect with the correct type."""
        effect = RemoveDocumentFromPatientEffect(document_id="123")
        result = effect.apply()
        assert result.type == EffectType.REMOVE_DOCUMENT_FROM_PATIENT

    def test_apply_returns_correct_payload(self) -> None:
        """Test that apply() returns an Effect with the correct payload."""
        effect = RemoveDocumentFromPatientEffect(document_id="123")
        result = effect.apply()
        payload = json.loads(result.payload)
        assert payload == {"document_id": "123"}

    def test_apply_with_patient_id(self) -> None:
        """Test that apply() includes patient_id in payload."""
        effect = RemoveDocumentFromPatientEffect(document_id="123", patient_id="patient789")
        result = effect.apply()
        payload = json.loads(result.payload)
        assert payload == {"document_id": "123", "patient_id": "patient789"}

    def test_apply_with_confidence_scores(self) -> None:
        """Test that apply() includes confidence_scores in payload."""
        effect = RemoveDocumentFromPatientEffect(document_id="123", confidence_scores={"123": 0.90})
        result = effect.apply()
        payload = json.loads(result.payload)
        assert payload == {"document_id": "123", "confidence_scores": {"123": 0.90}}

    def test_validation_confidence_score_out_of_range_low(self) -> None:
        """Test that confidence_scores values below 0.0 raise ValidationError."""
        effect = RemoveDocumentFromPatientEffect(document_id="123", confidence_scores={"123": -0.1})
        with pytest.raises(ValidationError) as exc_info:
            effect.apply()
        assert "must be between 0.0 and 1.0" in str(exc_info.value)

    def test_validation_confidence_score_out_of_range_high(self) -> None:
        """Test that confidence_scores values above 1.0 raise ValidationError."""
        effect = RemoveDocumentFromPatientEffect(document_id="123", confidence_scores={"123": 1.5})
        with pytest.raises(ValidationError) as exc_info:
            effect.apply()
        assert "must be between 0.0 and 1.0" in str(exc_info.value)

    def test_validation_confidence_score_key_mismatch(self) -> None:
        """Test that confidence_scores keys not matching document_id raise ValidationError."""
        effect = RemoveDocumentFromPatientEffect(document_id="123", confidence_scores={"456": 0.85})
        with pytest.raises(ValidationError) as exc_info:
            effect.apply()
        assert "does not match document_id" in str(exc_info.value)

    def test_validation_confidence_score_boundary_zero(self) -> None:
        """Test that confidence_scores value of 0.0 is valid."""
        effect = RemoveDocumentFromPatientEffect(document_id="123", confidence_scores={"123": 0.0})
        result = effect.apply()
        payload = json.loads(result.payload)
        assert payload["confidence_scores"] == {"123": 0.0}

    def test_validation_confidence_score_boundary_one(self) -> None:
        """Test that confidence_scores value of 1.0 is valid."""
        effect = RemoveDocumentFromPatientEffect(document_id="123", confidence_scores={"123": 1.0})
        result = effect.apply()
        payload = json.loads(result.payload)
        assert payload["confidence_scores"] == {"123": 1.0}

    def test_document_id_required(self) -> None:
        """Test that document_id is required."""
        with pytest.raises(ValidationError):
            RemoveDocumentFromPatientEffect()  # type: ignore[call-arg]

    def test_meta_effect_type(self) -> None:
        """Test that Meta.effect_type is correct."""
        assert (
            RemoveDocumentFromPatientEffect.Meta.effect_type
            == EffectType.REMOVE_DOCUMENT_FROM_PATIENT
        )
