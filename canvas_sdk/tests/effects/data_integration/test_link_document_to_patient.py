import json
from datetime import date

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.data_integration import (
    LinkDocumentConfidenceScores,
    LinkDocumentToPatient,
)
from canvas_sdk.effects.data_integration.link_document_to_patient import CONFIDENCE_SCORE_KEYS


class TestLinkDocumentToPatientEffectCreation:
    """Tests for effect creation and basic functionality."""

    def test_create_effect_with_all_required_fields(self) -> None:
        """Test creating effect with all required fields succeeds."""
        effect = LinkDocumentToPatient(
            first_name="John",
            last_name="Doe",
            date_of_birth=date(1990, 5, 15),
            document_id="12345",
        )
        applied = effect.apply()

        assert applied.type == EffectType.LINK_DOCUMENT_TO_PATIENT

        payload = json.loads(applied.payload)
        assert payload["data"]["first_name"] == "John"
        assert payload["data"]["last_name"] == "Doe"
        assert payload["data"]["date_of_birth"] == "1990-05-15"
        assert payload["data"]["document_id"] == "12345"
        assert "confidence_scores" not in payload["data"]

    def test_create_effect_with_integer_document_id(self) -> None:
        """Test creating effect with integer document_id succeeds."""
        effect = LinkDocumentToPatient(
            first_name="Jane",
            last_name="Smith",
            date_of_birth=date(1985, 12, 1),
            document_id=42,
        )
        applied = effect.apply()

        payload = json.loads(applied.payload)
        assert payload["data"]["document_id"] == "42"

    def test_create_effect_with_confidence_scores(self) -> None:
        """Test creating effect with confidence_scores succeeds."""
        effect = LinkDocumentToPatient(
            first_name="John",
            last_name="Doe",
            date_of_birth=date(1990, 5, 15),
            document_id="12345",
            confidence_scores={
                "first_name": 0.95,
                "last_name": 0.90,
                "date_of_birth": 0.85,
            },
        )
        applied = effect.apply()

        payload = json.loads(applied.payload)
        assert payload["data"]["confidence_scores"] == {
            "first_name": 0.95,
            "last_name": 0.90,
            "date_of_birth": 0.85,
        }

    def test_create_effect_with_all_confidence_scores(self) -> None:
        """Test creating effect with all confidence_scores keys."""
        effect = LinkDocumentToPatient(
            first_name="John",
            last_name="Doe",
            date_of_birth=date(1990, 5, 15),
            document_id="12345",
            confidence_scores={
                "first_name": 0.95,
                "last_name": 0.90,
                "date_of_birth": 0.85,
            },
        )
        applied = effect.apply()

        payload = json.loads(applied.payload)
        assert len(payload["data"]["confidence_scores"]) == 3


class TestLinkDocumentToPatientValuesProperty:
    """Tests for the values property output."""

    def test_values_property_returns_correct_structure(self) -> None:
        """Test values property returns correctly structured dict."""
        effect = LinkDocumentToPatient(
            first_name="John",
            last_name="Doe",
            date_of_birth=date(1990, 5, 15),
            document_id="12345",
        )

        values = effect.values

        assert values == {
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1990-05-15",
            "document_id": "12345",
        }

    def test_values_property_with_confidence_scores(self) -> None:
        """Test values property includes confidence_scores when provided."""
        effect = LinkDocumentToPatient(
            first_name="John",
            last_name="Doe",
            date_of_birth=date(1990, 5, 15),
            document_id="12345",
            confidence_scores={"first_name": 0.9},
        )

        values = effect.values

        assert "confidence_scores" in values
        assert values["confidence_scores"] == {"first_name": 0.9}

    def test_values_property_excludes_none_confidence_scores(self) -> None:
        """Test values property excludes confidence_scores when None."""
        effect = LinkDocumentToPatient(
            first_name="John",
            last_name="Doe",
            date_of_birth=date(1990, 5, 15),
            document_id="12345",
            confidence_scores=None,
        )

        values = effect.values

        assert "confidence_scores" not in values


class TestLinkDocumentToPatientRequiredFieldValidation:
    """Tests for required field validation errors."""

    def test_apply_raises_error_when_first_name_missing(self) -> None:
        """Test apply raises error when first_name is missing."""
        effect = LinkDocumentToPatient(
            last_name="Doe",
            date_of_birth=date(1990, 5, 15),
            document_id="12345",
        )
        with pytest.raises(ValidationError) as exc_info:
            effect.apply()

        assert "first_name" in str(exc_info.value)

    def test_apply_raises_error_when_last_name_missing(self) -> None:
        """Test apply raises error when last_name is missing."""
        effect = LinkDocumentToPatient(
            first_name="John",
            date_of_birth=date(1990, 5, 15),
            document_id="12345",
        )
        with pytest.raises(ValidationError) as exc_info:
            effect.apply()

        assert "last_name" in str(exc_info.value)

    def test_apply_raises_error_when_date_of_birth_missing(self) -> None:
        """Test apply raises error when date_of_birth is missing."""
        effect = LinkDocumentToPatient(
            first_name="John",
            last_name="Doe",
            document_id="12345",
        )
        with pytest.raises(ValidationError) as exc_info:
            effect.apply()

        assert "date_of_birth" in str(exc_info.value)

    def test_apply_raises_error_when_document_id_missing(self) -> None:
        """Test apply raises error when document_id is missing."""
        effect = LinkDocumentToPatient(
            first_name="John",
            last_name="Doe",
            date_of_birth=date(1990, 5, 15),
        )
        with pytest.raises(ValidationError) as exc_info:
            effect.apply()

        assert "document_id" in str(exc_info.value)

    def test_apply_raises_error_when_all_required_fields_missing(self) -> None:
        """Test apply raises error when all required fields are missing."""
        effect = LinkDocumentToPatient()
        with pytest.raises(ValidationError) as exc_info:
            effect.apply()

        err_msg = str(exc_info.value)
        assert "first_name" in err_msg
        assert "last_name" in err_msg
        assert "date_of_birth" in err_msg
        assert "document_id" in err_msg


class TestLinkDocumentToPatientNameValidation:
    """Tests for name field validation (empty string checks)."""

    def test_apply_raises_error_when_first_name_is_empty(self) -> None:
        """Test apply raises error when first_name is empty string."""
        effect = LinkDocumentToPatient(
            first_name="",
            last_name="Doe",
            date_of_birth=date(1990, 5, 15),
            document_id="12345",
        )
        with pytest.raises(ValidationError) as exc_info:
            effect.apply()

        assert "first_name must be a non-empty string" in str(exc_info.value)

    def test_apply_raises_error_when_first_name_is_whitespace(self) -> None:
        """Test apply raises error when first_name is only whitespace."""
        effect = LinkDocumentToPatient(
            first_name="   ",
            last_name="Doe",
            date_of_birth=date(1990, 5, 15),
            document_id="12345",
        )
        with pytest.raises(ValidationError) as exc_info:
            effect.apply()

        assert "first_name must be a non-empty string" in str(exc_info.value)

    def test_apply_raises_error_when_last_name_is_empty(self) -> None:
        """Test apply raises error when last_name is empty string."""
        effect = LinkDocumentToPatient(
            first_name="John",
            last_name="",
            date_of_birth=date(1990, 5, 15),
            document_id="12345",
        )
        with pytest.raises(ValidationError) as exc_info:
            effect.apply()

        assert "last_name must be a non-empty string" in str(exc_info.value)

    def test_apply_raises_error_when_last_name_is_whitespace(self) -> None:
        """Test apply raises error when last_name is only whitespace."""
        effect = LinkDocumentToPatient(
            first_name="John",
            last_name="\t\n",
            date_of_birth=date(1990, 5, 15),
            document_id="12345",
        )
        with pytest.raises(ValidationError) as exc_info:
            effect.apply()

        assert "last_name must be a non-empty string" in str(exc_info.value)


class TestLinkDocumentToPatientDocumentIdValidation:
    """Tests for document_id field validation."""

    def test_apply_raises_error_when_document_id_is_empty(self) -> None:
        """Test apply raises error when document_id is empty string."""
        effect = LinkDocumentToPatient(
            first_name="John",
            last_name="Doe",
            date_of_birth=date(1990, 5, 15),
            document_id="",
        )
        with pytest.raises(ValidationError) as exc_info:
            effect.apply()

        assert "document_id must be a non-empty string" in str(exc_info.value)

    def test_apply_raises_error_when_document_id_is_whitespace(self) -> None:
        """Test apply raises error when document_id is only whitespace."""
        effect = LinkDocumentToPatient(
            first_name="John",
            last_name="Doe",
            date_of_birth=date(1990, 5, 15),
            document_id="   ",
        )
        with pytest.raises(ValidationError) as exc_info:
            effect.apply()

        assert "document_id must be a non-empty string" in str(exc_info.value)


class TestLinkDocumentToPatientWhitespaceNormalization:
    """Tests for whitespace normalization in serialization."""

    def test_values_strips_whitespace_from_first_name(self) -> None:
        """Test values property strips leading/trailing whitespace from first_name."""
        effect = LinkDocumentToPatient(
            first_name="  John  ",
            last_name="Doe",
            date_of_birth=date(1990, 5, 15),
            document_id="12345",
        )
        applied = effect.apply()

        payload = json.loads(applied.payload)
        assert payload["data"]["first_name"] == "John"

    def test_values_strips_whitespace_from_last_name(self) -> None:
        """Test values property strips leading/trailing whitespace from last_name."""
        effect = LinkDocumentToPatient(
            first_name="John",
            last_name="\tDoe\n",
            date_of_birth=date(1990, 5, 15),
            document_id="12345",
        )
        applied = effect.apply()

        payload = json.loads(applied.payload)
        assert payload["data"]["last_name"] == "Doe"

    def test_values_strips_whitespace_from_document_id(self) -> None:
        """Test values property strips whitespace from document_id."""
        effect = LinkDocumentToPatient(
            first_name="John",
            last_name="Doe",
            date_of_birth=date(1990, 5, 15),
            document_id=" 12345 ",
        )
        applied = effect.apply()

        payload = json.loads(applied.payload)
        assert payload["data"]["document_id"] == "12345"


class TestLinkDocumentToPatientLinkDocumentConfidenceScoresValidation:
    """Tests for confidence_scores validation."""

    def test_creation_raises_error_for_invalid_confidence_scores_key(self) -> None:
        """Test creation raises error for invalid keys in confidence_scores.

        The model_validator catches invalid keys before Pydantic processes
        the TypedDict (which would otherwise silently drop unknown keys).
        """
        with pytest.raises(ValidationError) as exc_info:
            LinkDocumentToPatient(
                first_name="John",
                last_name="Doe",
                date_of_birth=date(1990, 5, 15),
                document_id="12345",
                confidence_scores={
                    "first_name": 0.9,
                    "invalid_key": 0.5,  # type: ignore[typeddict-unknown-key]
                },
            )

        err_msg = str(exc_info.value)
        assert "invalid keys" in err_msg
        assert "invalid_key" in err_msg

    def test_creation_raises_error_for_multiple_invalid_keys(self) -> None:
        """Test creation raises error for multiple invalid keys."""
        with pytest.raises(ValidationError) as exc_info:
            LinkDocumentToPatient(
                first_name="John",
                last_name="Doe",
                date_of_birth=date(1990, 5, 15),
                document_id="12345",
                confidence_scores={
                    "first_name": 0.9,
                    "bad_key_1": 0.5,  # type: ignore[typeddict-unknown-key]
                    "bad_key_2": 0.7,  # type: ignore[typeddict-unknown-key]
                },
            )

        err_msg = str(exc_info.value)
        assert "bad_key_1" in err_msg
        assert "bad_key_2" in err_msg

    def test_creation_raises_error_when_confidence_score_below_zero(self) -> None:
        """Test creation raises error when confidence score is below 0.

        Pydantic validates the range constraint at construction time via
        the Annotated[float, Field(ge=0.0, le=1.0)] type annotation.
        """
        with pytest.raises(ValidationError) as exc_info:
            LinkDocumentToPatient(
                first_name="John",
                last_name="Doe",
                date_of_birth=date(1990, 5, 15),
                document_id="12345",
                confidence_scores={"first_name": -0.1},
            )

        err_msg = str(exc_info.value)
        assert "greater_than_equal" in err_msg or "greater than or equal to 0" in err_msg

    def test_creation_raises_error_when_confidence_score_above_one(self) -> None:
        """Test creation raises error when confidence score is above 1.0.

        Pydantic validates the range constraint at construction time via
        the Annotated[float, Field(ge=0.0, le=1.0)] type annotation.
        """
        with pytest.raises(ValidationError) as exc_info:
            LinkDocumentToPatient(
                first_name="John",
                last_name="Doe",
                date_of_birth=date(1990, 5, 15),
                document_id="12345",
                confidence_scores={"last_name": 1.5},
            )

        err_msg = str(exc_info.value)
        assert "less_than_equal" in err_msg or "less than or equal to 1" in err_msg

    def test_creation_raises_error_when_confidence_score_is_not_numeric(self) -> None:
        """Test creation raises error when confidence score is not a number.

        Pydantic validates types at construction time, so this error happens
        during effect creation rather than during apply().
        """
        with pytest.raises(ValidationError) as exc_info:
            LinkDocumentToPatient(
                first_name="John",
                last_name="Doe",
                date_of_birth=date(1990, 5, 15),
                document_id="12345",
                confidence_scores={"first_name": "high"},  # type: ignore[dict-item]
            )

        err_msg = str(exc_info.value)
        assert "float_type" in err_msg or "valid number" in err_msg

    def test_apply_succeeds_with_boundary_confidence_scores(self) -> None:
        """Test apply succeeds with boundary values 0.0 and 1.0."""
        effect = LinkDocumentToPatient(
            first_name="John",
            last_name="Doe",
            date_of_birth=date(1990, 5, 15),
            document_id="12345",
            confidence_scores={
                "first_name": 0.0,
                "last_name": 1.0,
            },
        )
        applied = effect.apply()

        payload = json.loads(applied.payload)
        assert payload["data"]["confidence_scores"]["first_name"] == 0.0
        assert payload["data"]["confidence_scores"]["last_name"] == 1.0

    def test_apply_accepts_integer_confidence_scores(self) -> None:
        """Test apply accepts integer values for confidence scores."""
        effect = LinkDocumentToPatient(
            first_name="John",
            last_name="Doe",
            date_of_birth=date(1990, 5, 15),
            document_id="12345",
            confidence_scores={"first_name": 1, "last_name": 0},
        )
        applied = effect.apply()

        payload = json.loads(applied.payload)
        assert payload["data"]["confidence_scores"]["first_name"] == 1
        assert payload["data"]["confidence_scores"]["last_name"] == 0


class TestLinkDocumentToPatientConstants:
    """Tests for module constants."""

    def test_confidence_score_keys_are_correct(self) -> None:
        """Test CONFIDENCE_SCORE_KEYS contains expected keys."""
        expected = {"first_name", "last_name", "date_of_birth"}
        assert expected == CONFIDENCE_SCORE_KEYS

    def test_confidence_score_keys_is_frozen(self) -> None:
        """Test CONFIDENCE_SCORE_KEYS is immutable."""
        assert isinstance(CONFIDENCE_SCORE_KEYS, frozenset)

    def test_confidence_score_keys_derived_from_typeddict(self) -> None:
        """Test CONFIDENCE_SCORE_KEYS matches LinkDocumentConfidenceScores TypedDict annotations."""
        assert frozenset(LinkDocumentConfidenceScores.__annotations__.keys()) == CONFIDENCE_SCORE_KEYS


class TestLinkDocumentConfidenceScoresTypedDict:
    """Tests for LinkDocumentConfidenceScores TypedDict."""

    def test_confidence_scores_accepts_valid_typed_dict(self) -> None:
        """Test that LinkDocumentConfidenceScores TypedDict works with valid values."""
        scores: LinkDocumentConfidenceScores = {
            "first_name": 0.95,
            "last_name": 0.90,
        }
        effect = LinkDocumentToPatient(
            first_name="John",
            last_name="Doe",
            date_of_birth=date(1990, 5, 15),
            document_id="12345",
            confidence_scores=scores,
        )
        applied = effect.apply()

        payload = json.loads(applied.payload)
        assert payload["data"]["confidence_scores"]["first_name"] == 0.95
        assert payload["data"]["confidence_scores"]["last_name"] == 0.90

    def test_confidence_scores_typeddict_has_all_expected_keys(self) -> None:
        """Test LinkDocumentConfidenceScores TypedDict defines all expected keys."""
        expected_keys = {"first_name", "last_name", "date_of_birth"}
        assert set(LinkDocumentConfidenceScores.__annotations__.keys()) == expected_keys

    def test_confidence_scores_typeddict_is_total_false(self) -> None:
        """Test LinkDocumentConfidenceScores TypedDict has total=False (all keys optional)."""
        # total=False means __required_keys__ should be empty
        assert not LinkDocumentConfidenceScores.__required_keys__
