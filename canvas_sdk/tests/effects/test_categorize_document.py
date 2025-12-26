import json
from typing import Any

import pytest
from pydantic import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.categorize_document import (
    CategorizeDocument,
    ConfidenceScores,
    DocumentType,
)


@pytest.fixture
def valid_document_type() -> DocumentType:
    """Valid document type for testing."""
    return {
        "key": "lab_report",
        "name": "Lab Report",
        "report_type": "CLINICAL",
        "template_type": "LabReportTemplate",
    }


@pytest.fixture
def valid_confidence_scores() -> ConfidenceScores:
    """Valid confidence scores for testing."""
    return {
        "document_id": 0.90,
        "document_type": {
            "key": 0.90,
            "name": 0.95,
            "report_type": 0.85,
            "template_type": 0.90,
        },
    }


class TestCategorizeDocumentCreation:
    """Tests for CategorizeDocument creation and basic properties."""

    def test_creation_with_valid_data(self, valid_document_type: DocumentType) -> None:
        """Test that CategorizeDocument can be created with valid data."""
        effect = CategorizeDocument(document_id="123", document_type=valid_document_type)
        assert effect.document_id == "123"
        assert effect.document_type == valid_document_type
        assert effect.confidence_scores is None

    def test_creation_with_int_document_id(self, valid_document_type: DocumentType) -> None:
        """Test that document_id can be an int and is serialized as string."""
        effect = CategorizeDocument(document_id=123, document_type=valid_document_type)
        assert effect.document_id == 123
        assert effect.values["document_id"] == "123"

    def test_creation_with_confidence_scores(
        self, valid_document_type: DocumentType, valid_confidence_scores: ConfidenceScores
    ) -> None:
        """Test that CategorizeDocument can be created with confidence_scores."""
        effect = CategorizeDocument(
            document_id="456",
            document_type=valid_document_type,
            confidence_scores=valid_confidence_scores,
        )
        assert effect.confidence_scores == valid_confidence_scores


class TestCategorizeDocumentValues:
    """Tests for the values property."""

    def test_values_with_confidence_scores(
        self, valid_document_type: DocumentType, valid_confidence_scores: ConfidenceScores
    ) -> None:
        """Test that values property includes confidence_scores when provided."""
        effect = CategorizeDocument(
            document_id=789,
            document_type=valid_document_type,
            confidence_scores=valid_confidence_scores,
        )
        values = effect.values
        assert values == {
            "document_id": "789",
            "document_type": valid_document_type,
            "confidence_scores": valid_confidence_scores,
        }

    def test_values_without_confidence_scores(self, valid_document_type: DocumentType) -> None:
        """Test that values property excludes confidence_scores when not provided."""
        effect = CategorizeDocument(document_id="999", document_type=valid_document_type)
        values = effect.values
        assert "confidence_scores" not in values
        assert values == {
            "document_id": "999",
            "document_type": valid_document_type,
        }


class TestCategorizeDocumentApply:
    """Tests for the apply method."""

    def test_apply_succeeds(self, valid_document_type: DocumentType) -> None:
        """Test that apply method succeeds with all required fields."""
        effect = CategorizeDocument(document_id="123", document_type=valid_document_type)
        applied = effect.apply()
        assert applied.type == EffectType.CATEGORIZE_DOCUMENT
        payload_data = json.loads(applied.payload)
        assert payload_data["document_id"] == "123"
        assert payload_data["document_type"] == valid_document_type

    @pytest.mark.parametrize("missing_field", ["document_id", "document_type"])
    def test_apply_raises_when_required_field_missing(
        self, missing_field: str, valid_document_type: DocumentType
    ) -> None:
        """Test that apply raises ValidationError when required field is missing."""
        kwargs = {"document_id": "123", "document_type": valid_document_type}
        kwargs.pop(missing_field)
        effect = CategorizeDocument(**kwargs)
        with pytest.raises(ValidationError) as exc_info:
            effect.apply()
        assert missing_field in repr(exc_info.value).lower()
        assert "required" in repr(exc_info.value).lower()


class TestDocumentTypeValidation:
    """Tests for document_type field validation."""

    def test_document_type_must_be_dict(self) -> None:
        """Test that document_type must be a dict."""
        with pytest.raises(ValidationError):
            CategorizeDocument(document_id="123", document_type="not_a_dict")  # type: ignore[arg-type]

    @pytest.mark.parametrize(
        "field,value,expected_error",
        [
            ("key", None, "document_type.key is required"),
            ("key", "", "document_type.key must be a non-empty string"),
            ("key", "   ", "document_type.key must be a non-empty string"),
            ("name", None, "document_type.name is required"),
            ("name", "", "document_type.name must be a non-empty string"),
            ("report_type", None, "document_type.report_type is required"),
        ],
    )
    def test_document_type_required_fields(
        self, field: str, value: Any, expected_error: str, valid_document_type: DocumentType
    ) -> None:
        """Test validation of required document_type fields."""
        document_type = valid_document_type.copy()
        if value is None:
            document_type.pop(field, None)
        else:
            document_type[field] = value
        effect = CategorizeDocument(document_id="123", document_type=document_type)
        with pytest.raises(ValidationError) as exc_info:
            effect.apply()
        assert expected_error in repr(exc_info.value)

    @pytest.mark.parametrize("report_type", ["CLINICAL", "ADMINISTRATIVE"])
    def test_valid_report_types(self, report_type: str) -> None:
        """Test that valid report types are accepted."""
        document_type: DocumentType = {
            "key": "test",
            "name": "Test",
            "report_type": report_type,
            "template_type": "LabReportTemplate" if report_type == "CLINICAL" else None,
        }
        effect = CategorizeDocument(document_id="123", document_type=document_type)
        applied = effect.apply()
        assert applied.type == EffectType.CATEGORIZE_DOCUMENT

    def test_invalid_report_type(self, valid_document_type: DocumentType) -> None:
        """Test that invalid report_type raises ValidationError."""
        document_type = valid_document_type.copy()
        document_type["report_type"] = "INVALID"
        effect = CategorizeDocument(document_id="123", document_type=document_type)
        with pytest.raises(ValidationError) as exc_info:
            effect.apply()
        assert "document_type.report_type must be one of" in repr(exc_info.value)

    @pytest.mark.parametrize(
        "template_type",
        ["LabReportTemplate", "ImagingReportTemplate", "SpecialtyReportTemplate", None],
    )
    def test_valid_template_types(self, template_type: str | None) -> None:
        """Test that valid template types are accepted."""
        document_type: DocumentType = {
            "key": "test",
            "name": "Test",
            "report_type": "CLINICAL" if template_type else "ADMINISTRATIVE",
            "template_type": template_type,
        }
        effect = CategorizeDocument(document_id="123", document_type=document_type)
        applied = effect.apply()
        assert applied.type == EffectType.CATEGORIZE_DOCUMENT

    def test_invalid_template_type(self, valid_document_type: DocumentType) -> None:
        """Test that invalid template_type raises ValidationError."""
        document_type = valid_document_type.copy()
        document_type["template_type"] = "InvalidTemplate"
        effect = CategorizeDocument(document_id="123", document_type=document_type)
        with pytest.raises(ValidationError) as exc_info:
            effect.apply()
        assert "document_type.template_type must be one of" in repr(exc_info.value)

    def test_template_type_must_be_string_or_null(self, valid_document_type: DocumentType) -> None:
        """Test that template_type must be string or null."""
        document_type = valid_document_type.copy()
        document_type["template_type"] = 123
        effect = CategorizeDocument(document_id="123", document_type=document_type)
        with pytest.raises(ValidationError) as exc_info:
            effect.apply()
        assert "document_type.template_type must be a string or null" in repr(exc_info.value)


class TestConfidenceScoresValidation:
    """Tests for confidence_scores field validation."""

    def test_invalid_top_level_keys(self, valid_document_type: DocumentType) -> None:
        """Test that invalid top-level confidence_scores keys raise ValueError."""
        invalid_scores = {"invalid_key": 0.5, "document_id": 0.9}
        with pytest.raises(ValueError, match="confidence_scores contains invalid keys"):
            CategorizeDocument(
                document_id="123",
                document_type=valid_document_type,
                confidence_scores=invalid_scores,  # type: ignore[arg-type]
            )

    def test_invalid_nested_keys(self, valid_document_type: DocumentType) -> None:
        """Test that invalid nested confidence_scores keys raise ValueError."""
        invalid_scores = {
            "document_id": 0.9,
            "document_type": {"invalid_key": 0.5, "key": 0.9},
        }
        with pytest.raises(
            ValueError, match="confidence_scores.document_type contains invalid keys"
        ):
            CategorizeDocument(
                document_id="123",
                document_type=valid_document_type,
                confidence_scores=invalid_scores,  # type: ignore[arg-type]
            )

    @pytest.mark.parametrize("value", [-0.1, 1.1])
    def test_out_of_range_values(self, value: float, valid_document_type: DocumentType) -> None:
        """Test that confidence_scores values outside 0.0-1.0 raise ValidationError."""
        if value < 0:
            invalid_scores: ConfidenceScores = {
                "document_id": value,
                "document_type": {
                    "key": 0.9,
                    "name": 0.95,
                    "report_type": 0.85,
                    "template_type": 0.9,
                },
            }
        else:
            invalid_scores: ConfidenceScores = {
                "document_id": 0.9,
                "document_type": {
                    "key": value,
                    "name": 0.95,
                    "report_type": 0.85,
                    "template_type": 0.9,
                },
            }
        with pytest.raises(ValidationError):
            CategorizeDocument(
                document_id="123",
                document_type=valid_document_type,
                confidence_scores=invalid_scores,
            )

    @pytest.mark.parametrize("value", [0.0, 1.0])
    def test_boundary_values(self, value: float, valid_document_type: DocumentType) -> None:
        """Test that confidence_scores boundary values (0.0, 1.0) are valid."""
        confidence_scores: ConfidenceScores = {
            "document_id": value,
            "document_type": {
                "key": value,
                "name": value,
                "report_type": value,
                "template_type": value,
            },
        }
        effect = CategorizeDocument(
            document_id="123",
            document_type=valid_document_type,
            confidence_scores=confidence_scores,
        )
        applied = effect.apply()
        assert applied.type == EffectType.CATEGORIZE_DOCUMENT

    def test_confidence_scores_must_be_dict(self, valid_document_type: DocumentType) -> None:
        """Test that confidence_scores must be a dict if provided."""
        with pytest.raises(ValidationError):
            CategorizeDocument(
                document_id="123",
                document_type=valid_document_type,
                confidence_scores="not_a_dict",  # type: ignore[arg-type]
            )

    def test_partial_confidence_scores(self, valid_document_type: DocumentType) -> None:
        """Test that confidence_scores can have only some keys."""
        partial_scores: ConfidenceScores = {"document_id": 0.9}
        effect = CategorizeDocument(
            document_id="123", document_type=valid_document_type, confidence_scores=partial_scores
        )
        applied = effect.apply()
        assert applied.type == EffectType.CATEGORIZE_DOCUMENT
        values = effect.values
        assert values["confidence_scores"]["document_id"] == 0.9
        assert "document_type" not in values["confidence_scores"]
