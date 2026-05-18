"""Tests for PrefillDocumentFields effect."""

import json

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.data_integration import PrefillDocumentFields
from canvas_sdk.effects.data_integration.types import AnnotationItem


def test_create_effect_with_all_required_fields() -> None:
    """Test creating effect with all required fields succeeds."""
    effect = PrefillDocumentFields(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        templates=[
            {
                "template_id": 620,
                "template_name": "Thyroid Profile With Tsh",
                "fields": {
                    "11580-8": {
                        "value": "2.35",
                        "unit": "uIU/mL",
                        "reference_range": "0.45 - 4.50",
                        "annotations": [AnnotationItem(text="AI 95%", color="#4CAF50")],
                    }
                },
            }
        ],
    )
    applied = effect.apply()

    assert applied.type == EffectType.UPDATE_DOCUMENT_FIELDS

    payload = json.loads(applied.payload)
    assert payload["data"]["document_id"] == "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    assert len(payload["data"]["templates"]) == 1
    assert payload["data"]["templates"][0]["template_id"] == 620


def test_create_effect_with_top_level_annotations() -> None:
    """Test creating effect with top-level annotations succeeds."""
    effect = PrefillDocumentFields(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        templates=[
            {
                "template_id": 620,
                "template_name": "Thyroid Profile",
                "fields": {"11580-8": {"value": "2.35"}},
            }
        ],
        annotations=[
            AnnotationItem(text="1 template matched", color="#2196F3"),
            AnnotationItem(text="1 field extracted", color="#4CAF50"),
        ],
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert len(payload["data"]["annotations"]) == 2
    assert payload["data"]["annotations"][0]["text"] == "1 template matched"


def test_create_effect_with_multiple_templates() -> None:
    """Test creating effect with multiple templates succeeds."""
    effect = PrefillDocumentFields(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        templates=[
            {
                "template_id": 620,
                "template_name": "Template 1",
                "fields": {"field1": {"value": "val1"}},
            },
            {
                "template_id": 621,
                "template_name": "Template 2",
                "fields": {"field2": {"value": "val2"}},
            },
        ],
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert len(payload["data"]["templates"]) == 2


def test_values_property_returns_correct_structure() -> None:
    """Test values property returns correctly structured dict."""
    effect = PrefillDocumentFields(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        templates=[
            {
                "template_id": 620,
                "template_name": "Test Template",
                "fields": {"field1": {"value": "val1"}},
            }
        ],
    )

    assert effect.values == {
        "document_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "templates": [
            {
                "template_id": 620,
                "template_name": "Test Template",
                "fields": {"field1": {"value": "val1"}},
            }
        ],
        "annotations": None,
        "source_protocol": None,
    }


def test_apply_succeeds_with_minimal_field() -> None:
    """Test apply succeeds when field has only value."""
    effect = PrefillDocumentFields(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        templates=[
            {
                "template_id": 620,
                "template_name": "Test",
                "fields": {"f1": {"value": "test_value"}},
            }
        ],
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["templates"][0]["fields"]["f1"]["value"] == "test_value"


def test_apply_succeeds_with_abnormal_field() -> None:
    """Test apply succeeds when field has abnormal flag."""
    effect = PrefillDocumentFields(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        templates=[
            {
                "template_id": 620,
                "template_name": "Test",
                "fields": {
                    "f1": {
                        "value": "150",
                        "unit": "mg/dL",
                        "reference_range": "70 - 100",
                        "abnormal": True,
                    }
                },
            }
        ],
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["templates"][0]["fields"]["f1"]["abnormal"] is True
