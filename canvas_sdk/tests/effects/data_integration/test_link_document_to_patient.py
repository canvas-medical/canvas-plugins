"""Tests for LinkDocumentToPatient effect."""

import json

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.data_integration import LinkDocumentToPatient


def test_create_effect_with_all_required_fields() -> None:
    """Test creating effect with all required fields succeeds."""
    effect = LinkDocumentToPatient(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        patient_key="patient-key-67890",
    )
    applied = effect.apply()

    assert applied.type == EffectType.LINK_DOCUMENT_TO_PATIENT

    payload = json.loads(applied.payload)
    assert payload["data"]["document_id"] == "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    assert payload["data"]["patient_key"] == "patient-key-67890"
    assert "annotations" not in payload["data"]
    assert "source_protocol" not in payload["data"]


def test_create_effect_with_integer_document_id() -> None:
    """Test creating effect with integer document_id succeeds."""
    effect = LinkDocumentToPatient(
        document_id=42,
        patient_key="patient-key-67890",
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["document_id"] == "42"


def test_create_effect_with_annotations() -> None:
    """Test creating effect with annotations succeeds."""
    effect = LinkDocumentToPatient(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        patient_key="patient-key-67890",
        annotations=[
            {"text": "AI 95%", "color": "#00AA00"},
            {"text": "DOB matched", "color": "#2196F3"},
        ],
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["annotations"] == [
        {"text": "AI 95%", "color": "#00AA00"},
        {"text": "DOB matched", "color": "#2196F3"},
    ]


def test_create_effect_with_source_protocol() -> None:
    """Test creating effect with source_protocol succeeds."""
    effect = LinkDocumentToPatient(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        patient_key="patient-key-67890",
        source_protocol="llm_v1",
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["source_protocol"] == "llm_v1"


def test_create_effect_with_all_optional_fields() -> None:
    """Test creating effect with all optional fields succeeds."""
    effect = LinkDocumentToPatient(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        patient_key="patient-key-67890",
        annotations=[
            {"text": "AI 95%", "color": "#00AA00"},
            {"text": "DOB matched", "color": "#2196F3"},
            {"text": "Name verified", "color": "#4CAF50"},
        ],
        source_protocol="llm_v1",
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["document_id"] == "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    assert payload["data"]["patient_key"] == "patient-key-67890"
    assert payload["data"]["annotations"] == [
        {"text": "AI 95%", "color": "#00AA00"},
        {"text": "DOB matched", "color": "#2196F3"},
        {"text": "Name verified", "color": "#4CAF50"},
    ]
    assert payload["data"]["source_protocol"] == "llm_v1"


def test_values_property_returns_correct_structure() -> None:
    """Test values property returns correctly structured dict."""
    effect = LinkDocumentToPatient(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        patient_key="patient-key-67890",
    )

    values = effect.values

    assert values == {
        "document_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "patient_key": "patient-key-67890",
    }


def test_values_property_with_annotations() -> None:
    """Test values property includes annotations when provided."""
    effect = LinkDocumentToPatient(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        patient_key="patient-key-67890",
        annotations=[{"text": "AI 95%", "color": "#00AA00"}],
    )

    values = effect.values

    assert "annotations" in values
    assert values["annotations"] == [{"text": "AI 95%", "color": "#00AA00"}]


def test_values_property_excludes_none_annotations() -> None:
    """Test values property excludes annotations when None."""
    effect = LinkDocumentToPatient(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        patient_key="patient-key-67890",
        annotations=None,
    )

    values = effect.values

    assert "annotations" not in values


def test_values_property_with_source_protocol() -> None:
    """Test values property includes source_protocol when provided."""
    effect = LinkDocumentToPatient(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        patient_key="patient-key-67890",
        source_protocol="llm_v1",
    )

    values = effect.values

    assert "source_protocol" in values
    assert values["source_protocol"] == "llm_v1"


def test_values_property_excludes_none_source_protocol() -> None:
    """Test values property excludes source_protocol when None."""
    effect = LinkDocumentToPatient(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        patient_key="patient-key-67890",
        source_protocol=None,
    )

    values = effect.values

    assert "source_protocol" not in values


def test_values_property_with_empty_annotations_list() -> None:
    """Test values property includes empty annotations list when explicitly set."""
    effect = LinkDocumentToPatient(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        patient_key="patient-key-67890",
        annotations=[],
    )

    values = effect.values

    assert "annotations" in values
    assert values["annotations"] == []


def test_apply_raises_error_when_document_id_missing() -> None:
    """Test apply raises error when document_id is missing."""
    effect = LinkDocumentToPatient(
        patient_key="patient-key-67890",
    )
    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    assert "document_id" in str(exc_info.value)


def test_apply_raises_error_when_patient_key_missing() -> None:
    """Test apply raises error when patient_key is missing."""
    effect = LinkDocumentToPatient(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    )
    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    assert "patient_key" in str(exc_info.value)


def test_apply_raises_error_when_all_required_fields_missing() -> None:
    """Test apply raises error when all required fields are missing."""
    effect = LinkDocumentToPatient()
    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    err_msg = str(exc_info.value)
    assert "document_id" in err_msg
    assert "patient_key" in err_msg


def test_apply_raises_error_when_document_id_is_empty() -> None:
    """Test apply raises error when document_id is empty string."""
    effect = LinkDocumentToPatient(
        document_id="",
        patient_key="patient-key-67890",
    )
    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    assert "document_id must be a non-empty string" in str(exc_info.value)


def test_apply_raises_error_when_document_id_is_whitespace() -> None:
    """Test apply raises error when document_id is only whitespace."""
    effect = LinkDocumentToPatient(
        document_id="   ",
        patient_key="patient-key-67890",
    )
    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    assert "document_id must be a non-empty string" in str(exc_info.value)


def test_apply_raises_error_when_patient_key_is_empty() -> None:
    """Test apply raises error when patient_key is empty string."""
    effect = LinkDocumentToPatient(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        patient_key="",
    )
    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    assert "patient_key must be a non-empty string" in str(exc_info.value)


def test_apply_raises_error_when_patient_key_is_whitespace() -> None:
    """Test apply raises error when patient_key is only whitespace."""
    effect = LinkDocumentToPatient(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        patient_key="   ",
    )
    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    assert "patient_key must be a non-empty string" in str(exc_info.value)


def test_values_strips_whitespace_from_document_id() -> None:
    """Test values property strips whitespace from document_id."""
    effect = LinkDocumentToPatient(
        document_id=" a1b2c3d4-e5f6-7890-abcd-ef1234567890 ",
        patient_key="patient-key-67890",
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["document_id"] == "a1b2c3d4-e5f6-7890-abcd-ef1234567890"


def test_values_strips_whitespace_from_patient_key() -> None:
    """Test values property strips whitespace from patient_key."""
    effect = LinkDocumentToPatient(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        patient_key=" patient-key-67890 ",
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["patient_key"] == "patient-key-67890"


def test_annotations_accepts_list_of_dicts() -> None:
    """Test annotations accepts a list of dicts with text and color."""
    effect = LinkDocumentToPatient(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        patient_key="patient-key-67890",
        annotations=[
            {"text": "Tag 1", "color": "#FF0000"},
            {"text": "Tag 2", "color": "#00FF00"},
            {"text": "Tag 3", "color": "#0000FF"},
        ],
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["annotations"] == [
        {"text": "Tag 1", "color": "#FF0000"},
        {"text": "Tag 2", "color": "#00FF00"},
        {"text": "Tag 3", "color": "#0000FF"},
    ]


def test_annotations_accepts_single_item_list() -> None:
    """Test annotations accepts a single-item list."""
    effect = LinkDocumentToPatient(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        patient_key="patient-key-67890",
        annotations=[{"text": "Only annotation", "color": "#FF0000"}],
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["annotations"] == [{"text": "Only annotation", "color": "#FF0000"}]


def test_annotations_preserves_order() -> None:
    """Test annotations preserves the order of items."""
    annotations = [
        {"text": "First", "color": "#FF0000"},
        {"text": "Second", "color": "#00FF00"},
        {"text": "Third", "color": "#0000FF"},
    ]
    effect = LinkDocumentToPatient(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        patient_key="patient-key-67890",
        annotations=annotations,
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["annotations"] == [
        {"text": "First", "color": "#FF0000"},
        {"text": "Second", "color": "#00FF00"},
        {"text": "Third", "color": "#0000FF"},
    ]


def test_annotations_with_color_only() -> None:
    """Test annotations can include color attribute."""
    effect = LinkDocumentToPatient(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        patient_key="patient-key-67890",
        annotations=[{"text": "Alert", "color": "#FF0000"}],
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["annotations"] == [{"text": "Alert", "color": "#FF0000"}]
