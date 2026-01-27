import json
from typing import Any

import pytest
from pydantic import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.categorize_document import (
    AnnotationItem,
    CategorizeDocument,
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
def valid_annotations() -> list[AnnotationItem]:
    """Valid annotations for testing."""
    return [
        AnnotationItem(text="AI 97%", color="#00FF00"),
        AnnotationItem(text="Auto-detected", color="#0000FF"),
    ]


class TestCategorizeDocumentCreation:
    """Tests for CategorizeDocument creation and basic properties."""

    def test_creation_with_valid_data(self, valid_document_type: DocumentType) -> None:
        """Test that CategorizeDocument can be created with valid data."""
        effect = CategorizeDocument(document_id="123", document_type=valid_document_type)
        assert effect.document_id == "123"
        assert effect.document_type == valid_document_type

    def test_creation_with_int_document_id(self, valid_document_type: DocumentType) -> None:
        """Test that document_id can be an int and is serialized as string."""
        effect = CategorizeDocument(document_id=123, document_type=valid_document_type)
        assert effect.document_id == 123
        assert effect.values["document_id"] == "123"


class TestCategorizeDocumentValues:
    """Tests for the values property."""

    def test_values_with_all_fields(
        self, valid_document_type: DocumentType, valid_annotations: list[AnnotationItem]
    ) -> None:
        """Test that values property includes all fields when provided."""
        effect = CategorizeDocument(
            document_id=789,
            document_type=valid_document_type,
            annotations=valid_annotations,
            source_protocol="test_plugin",
        )
        values = effect.values
        assert values == {
            "document_id": "789",
            "document_type": valid_document_type,
            "annotations": valid_annotations,
            "source_protocol": "test_plugin",
        }

    def test_values_without_optional_fields(self, valid_document_type: DocumentType) -> None:
        """Test that values property excludes optional fields when not provided."""
        effect = CategorizeDocument(document_id="999", document_type=valid_document_type)
        values = effect.values
        assert "annotations" not in values
        assert "source_protocol" not in values
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
        kwargs: dict[str, Any] = {"document_id": "123", "document_type": valid_document_type}
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
        document_type: dict[str, Any] = dict(valid_document_type)
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
        document_type: dict[str, Any] = dict(valid_document_type)
        document_type["template_type"] = 123
        effect = CategorizeDocument(document_id="123", document_type=document_type)
        with pytest.raises(ValidationError) as exc_info:
            effect.apply()
        assert "document_type.template_type must be a string or null" in repr(exc_info.value)


class TestAnnotationsAndSourceProtocol:
    """Tests for annotations and source_protocol fields."""

    def test_annotations_included_in_payload(
        self, valid_document_type: DocumentType, valid_annotations: list[AnnotationItem]
    ) -> None:
        """Test that annotations are included in effect payload."""
        effect = CategorizeDocument(
            document_id="test-uuid",
            document_type=valid_document_type,
            annotations=valid_annotations,
        )
        assert effect.values["annotations"] == valid_annotations

    def test_source_protocol_included_in_payload(self, valid_document_type: DocumentType) -> None:
        """Test that source_protocol is included in effect payload."""
        effect = CategorizeDocument(
            document_id="test-uuid",
            document_type=valid_document_type,
            source_protocol="llm_v1",
        )
        assert effect.values["source_protocol"] == "llm_v1"

    def test_annotations_and_source_protocol_omitted_when_none(
        self, valid_document_type: DocumentType
    ) -> None:
        """Test that None values are not included in payload."""
        effect = CategorizeDocument(
            document_id="test-uuid",
            document_type=valid_document_type,
        )
        assert "annotations" not in effect.values
        assert "source_protocol" not in effect.values

    def test_annotations_and_source_protocol_in_applied_payload(
        self, valid_document_type: DocumentType
    ) -> None:
        """Test that annotations and source_protocol appear in applied payload."""
        annotations: list[AnnotationItem] = [AnnotationItem(text="AI 95%", color="#00FF00")]
        effect = CategorizeDocument(
            document_id="test-uuid",
            document_type=valid_document_type,
            annotations=annotations,
            source_protocol="test_plugin",
        )
        applied = effect.apply()
        payload_data = json.loads(applied.payload)
        assert payload_data["annotations"] == annotations
        assert payload_data["source_protocol"] == "test_plugin"

    def test_empty_annotations_list_included(self, valid_document_type: DocumentType) -> None:
        """Test that an empty annotations list is included in payload when explicitly set."""
        effect = CategorizeDocument(
            document_id="test-uuid",
            document_type=valid_document_type,
            annotations=[],
        )
        assert effect.values["annotations"] == []

    def test_all_fields_together(
        self,
        valid_document_type: DocumentType,
        valid_annotations: list[AnnotationItem],
    ) -> None:
        """Test that all fields work together."""
        effect = CategorizeDocument(
            document_id="test-uuid",
            document_type=valid_document_type,
            annotations=valid_annotations,
            source_protocol="llm_v1",
        )
        values = effect.values
        assert values["document_id"] == "test-uuid"
        assert values["document_type"] == valid_document_type
        assert values["annotations"] == valid_annotations
        assert values["source_protocol"] == "llm_v1"
