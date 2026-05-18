import json

import pytest

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.data_integration import CategorizeDocument
from canvas_sdk.effects.data_integration.types import (
    AnnotationItem,
    DocumentType,
    ReportType,
    TemplateType,
)


@pytest.fixture
def valid_document_type() -> DocumentType:
    """Valid document type for testing."""
    return {
        "key": "lab_report",
        "name": "Lab Report",
        "report_type": ReportType.CLINICAL,
        "template_type": TemplateType.LAB_REPORT,
    }


@pytest.fixture
def valid_annotations() -> list[AnnotationItem]:
    """Valid annotations for testing."""
    return [
        AnnotationItem(text="AI 97%", color="#00FF00"),
        AnnotationItem(text="Auto-detected", color="#0000FF"),
    ]


def test_creation_with_valid_data(valid_document_type: DocumentType) -> None:
    """Test that CategorizeDocument can be created with valid data."""
    effect = CategorizeDocument(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890", document_type=valid_document_type
    )
    assert str(effect.document_id) == "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    assert effect.document_type == valid_document_type


def test_values_with_all_fields(
    valid_document_type: DocumentType, valid_annotations: list[AnnotationItem]
) -> None:
    """Test that values property includes all fields when provided."""
    effect = CategorizeDocument(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        document_type=valid_document_type,
        annotations=valid_annotations,
        source_protocol="test_plugin",
    )
    values = effect.values
    assert values == {
        "document_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "document_type": valid_document_type,
        "annotations": valid_annotations,
        "source_protocol": "test_plugin",
    }


def test_values_without_optional_fields(valid_document_type: DocumentType) -> None:
    """Test that values property emits None for unset optional fields."""
    effect = CategorizeDocument(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890", document_type=valid_document_type
    )
    assert effect.values == {
        "document_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "document_type": valid_document_type,
        "annotations": None,
        "source_protocol": None,
    }


def test_apply_succeeds(valid_document_type: DocumentType) -> None:
    """Test that apply method succeeds with all required fields."""
    effect = CategorizeDocument(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890", document_type=valid_document_type
    )
    applied = effect.apply()
    assert applied.type == EffectType.CATEGORIZE_DOCUMENT
    payload = json.loads(applied.payload)
    assert payload["data"]["document_id"] == "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    assert payload["data"]["document_type"] == valid_document_type
