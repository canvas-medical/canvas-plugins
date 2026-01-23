"""Tests for PrefillDocumentFields effect."""

import json
from typing import Any, cast

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.data_integration import PrefillDocumentFields


def test_create_effect_with_all_required_fields() -> None:
    """Test creating effect with all required fields succeeds."""
    effect = PrefillDocumentFields(
        document_id="12345",
        templates=[
            {
                "templateId": 620,
                "templateName": "Thyroid Profile With Tsh",
                "fields": {
                    "11580-8": {
                        "value": "2.35",
                        "unit": "uIU/mL",
                        "referenceRange": "0.45 - 4.50",
                        "annotations": [{"text": "AI 95%", "color": "#4CAF50"}],
                    }
                },
            }
        ],
    )
    applied = effect.apply()

    assert applied.type == EffectType.UPDATE_DOCUMENT_FIELDS

    payload = json.loads(applied.payload)
    assert payload["data"]["document_id"] == "12345"
    assert len(payload["data"]["templates"]) == 1
    assert payload["data"]["templates"][0]["templateId"] == 620


def test_create_effect_with_top_level_annotations() -> None:
    """Test creating effect with top-level annotations succeeds."""
    effect = PrefillDocumentFields(
        document_id="12345",
        templates=[
            {
                "templateId": 620,
                "templateName": "Thyroid Profile",
                "fields": {"11580-8": {"value": "2.35"}},
            }
        ],
        annotations=[
            {"text": "1 template matched", "color": "#2196F3"},
            {"text": "1 field extracted", "color": "#4CAF50"},
        ],
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert len(payload["data"]["annotations"]) == 2
    assert payload["data"]["annotations"][0]["text"] == "1 template matched"


def test_create_effect_with_multiple_templates() -> None:
    """Test creating effect with multiple templates succeeds."""
    effect = PrefillDocumentFields(
        document_id="12345",
        templates=[
            {
                "templateId": 620,
                "templateName": "Template 1",
                "fields": {"field1": {"value": "val1"}},
            },
            {
                "templateId": 621,
                "templateName": "Template 2",
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
        document_id="12345",
        templates=[
            {
                "templateId": 620,
                "templateName": "Test Template",
                "fields": {"field1": {"value": "val1"}},
            }
        ],
    )

    values = effect.values

    assert values["document_id"] == "12345"
    assert "templates" in values
    assert values["templates"][0]["templateId"] == 620


def test_values_property_excludes_none_annotations() -> None:
    """Test values property excludes annotations when None."""
    effect = PrefillDocumentFields(
        document_id="12345",
        templates=[
            {
                "templateId": 620,
                "templateName": "Test Template",
                "fields": {"field1": {"value": "val1"}},
            }
        ],
        annotations=None,
    )

    values = effect.values

    assert "annotations" not in values


def test_apply_raises_error_when_document_id_missing() -> None:
    """Test apply raises error when document_id is missing."""
    effect = PrefillDocumentFields(
        templates=[
            {
                "templateId": 620,
                "templateName": "Test",
                "fields": {"f1": {"value": "v1"}},
            }
        ],
    )
    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    assert "document_id" in str(exc_info.value)


def test_apply_raises_error_when_templates_missing() -> None:
    """Test apply raises error when templates is missing."""
    effect = PrefillDocumentFields(document_id="12345")
    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    assert "templates" in str(exc_info.value)


def test_apply_raises_error_when_templates_empty() -> None:
    """Test apply raises error when templates is empty list."""
    effect = PrefillDocumentFields(document_id="12345", templates=[])
    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    assert "templates" in str(exc_info.value)


def test_apply_raises_error_when_document_id_is_empty() -> None:
    """Test apply raises error when document_id is empty string."""
    effect = PrefillDocumentFields(
        document_id="",
        templates=[
            {
                "templateId": 620,
                "templateName": "Test",
                "fields": {"f1": {"value": "v1"}},
            }
        ],
    )
    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    assert "document_id must be a non-empty string" in str(exc_info.value)


def test_apply_raises_error_when_document_id_is_whitespace() -> None:
    """Test apply raises error when document_id is only whitespace."""
    effect = PrefillDocumentFields(
        document_id="   ",
        templates=[
            {
                "templateId": 620,
                "templateName": "Test",
                "fields": {"f1": {"value": "v1"}},
            }
        ],
    )
    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    assert "document_id must be a non-empty string" in str(exc_info.value)


def test_apply_raises_error_when_template_missing_id() -> None:
    """Test apply raises error when template missing templateId."""
    effect = PrefillDocumentFields(
        document_id="12345",
        templates=[
            {
                "templateName": "Test",
                "fields": {"f1": {"value": "v1"}},
            }
        ],
    )
    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    assert (
        "templateid" in str(exc_info.value).lower() or "template_id" in str(exc_info.value).lower()
    )


def test_apply_raises_error_when_template_missing_name() -> None:
    """Test apply raises error when template missing templateName."""
    effect = PrefillDocumentFields(
        document_id="12345",
        templates=[
            {
                "templateId": 620,
                "fields": {"f1": {"value": "v1"}},
            }
        ],
    )
    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    assert (
        "templatename" in str(exc_info.value).lower()
        or "template_name" in str(exc_info.value).lower()
    )


def test_apply_raises_error_when_template_name_empty() -> None:
    """Test apply raises error when templateName is empty."""
    effect = PrefillDocumentFields(
        document_id="12345",
        templates=[
            {
                "templateId": 620,
                "templateName": "",
                "fields": {"f1": {"value": "v1"}},
            }
        ],
    )
    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    assert (
        "templatename" in str(exc_info.value).lower()
        or "template_name" in str(exc_info.value).lower()
    )


def test_apply_raises_error_when_field_missing_value() -> None:
    """Test apply raises error when field missing value key."""
    effect = PrefillDocumentFields(
        document_id="12345",
        templates=[
            {
                "templateId": 620,
                "templateName": "Test",
                "fields": {"f1": {"unit": "mg"}},
            }
        ],
    )
    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    assert "value" in str(exc_info.value).lower()


def test_apply_succeeds_with_minimal_field() -> None:
    """Test apply succeeds when field has only value."""
    effect = PrefillDocumentFields(
        document_id="12345",
        templates=[
            {
                "templateId": 620,
                "templateName": "Test",
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
        document_id="12345",
        templates=[
            {
                "templateId": 620,
                "templateName": "Test",
                "fields": {
                    "f1": {
                        "value": "150",
                        "unit": "mg/dL",
                        "referenceRange": "70 - 100",
                        "abnormal": True,
                    }
                },
            }
        ],
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["templates"][0]["fields"]["f1"]["abnormal"] is True


def test_apply_raises_error_when_annotation_missing_text() -> None:
    """Test apply raises error when annotation missing text."""
    with pytest.raises(ValidationError) as exc_info:
        PrefillDocumentFields(
            document_id="12345",
            templates=[
                {
                    "templateId": 620,
                    "templateName": "Test",
                    "fields": {"f1": {"value": "v1"}},
                }
            ],
            annotations=cast(Any, [{"color": "#FF0000"}]),
        )

    assert "text" in str(exc_info.value).lower()


def test_apply_raises_error_when_annotation_missing_color() -> None:
    """Test apply raises error when annotation missing color."""
    with pytest.raises(ValidationError) as exc_info:
        PrefillDocumentFields(
            document_id="12345",
            templates=[
                {
                    "templateId": 620,
                    "templateName": "Test",
                    "fields": {"f1": {"value": "v1"}},
                }
            ],
            annotations=cast(Any, [{"text": "AI 95%"}]),
        )

    assert "color" in str(exc_info.value).lower()


def test_apply_raises_error_when_field_annotation_missing_text() -> None:
    """Test apply raises error when field annotation missing text."""
    effect = PrefillDocumentFields(
        document_id="12345",
        templates=[
            {
                "templateId": 620,
                "templateName": "Test",
                "fields": {
                    "f1": {
                        "value": "v1",
                        "annotations": [{"color": "#FF0000"}],
                    }
                },
            }
        ],
    )
    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    assert "text" in str(exc_info.value).lower()
