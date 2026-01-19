"""Tests for AssignDocumentReviewer effect."""

import json

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.data_integration import (
    Annotation,
    AssignDocumentReviewer,
    Priority,
    ReviewMode,
)


def test_annotation_creation() -> None:
    """Test creating an Annotation with text and color."""
    annotation = Annotation(text="Team lead", color="#FF0000")
    assert annotation.text == "Team lead"
    assert annotation.color == "#FF0000"


def test_annotation_model_dump() -> None:
    """Test Annotation model_dump returns correct dict."""
    annotation = Annotation(text="Primary care", color="#00FF00")
    assert annotation.model_dump() == {"text": "Primary care", "color": "#00FF00"}


def test_annotation_requires_text() -> None:
    """Test that Annotation requires text field."""
    with pytest.raises(ValidationError):
        Annotation(color="#FF0000")  # type: ignore[call-arg]


def test_annotation_requires_color() -> None:
    """Test that Annotation requires color field."""
    with pytest.raises(ValidationError):
        Annotation(text="Test")  # type: ignore[call-arg]


def test_create_effect_with_document_id_only() -> None:
    """Test creating effect with only document_id succeeds."""
    effect = AssignDocumentReviewer(document_id="12345")
    applied = effect.apply()

    assert applied.type == EffectType.ASSIGN_DOCUMENT_REVIEWER

    payload = json.loads(applied.payload)
    assert payload["data"]["document_id"] == "12345"
    assert payload["data"]["priority"] is False
    assert payload["data"]["review_mode"] == "RR"
    assert "reviewer_id" not in payload["data"]
    assert "team_id" not in payload["data"]


def test_create_effect_with_reviewer_id() -> None:
    """Test creating effect with reviewer_id succeeds."""
    effect = AssignDocumentReviewer(
        document_id="12345",
        reviewer_id="staff-key-123",
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["reviewer_id"] == "staff-key-123"


def test_create_effect_with_team_id() -> None:
    """Test creating effect with team_id succeeds."""
    effect = AssignDocumentReviewer(
        document_id="12345",
        team_id="team-uuid-456",
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["team_id"] == "team-uuid-456"


def test_create_effect_with_both_reviewer_and_team() -> None:
    """Test creating effect with both reviewer_id and team_id succeeds."""
    effect = AssignDocumentReviewer(
        document_id="12345",
        reviewer_id="staff-key-123",
        team_id="team-uuid-456",
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["reviewer_id"] == "staff-key-123"
    assert payload["data"]["team_id"] == "team-uuid-456"


def test_create_effect_with_integer_document_id() -> None:
    """Test creating effect with integer document_id succeeds."""
    effect = AssignDocumentReviewer(document_id=42)
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["document_id"] == "42"


def test_create_effect_with_integer_reviewer_id() -> None:
    """Test creating effect with integer reviewer_id succeeds."""
    effect = AssignDocumentReviewer(
        document_id="12345",
        reviewer_id=123,
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["reviewer_id"] == "123"


def test_create_effect_with_high_priority() -> None:
    """Test creating effect with HIGH priority succeeds."""
    effect = AssignDocumentReviewer(
        document_id="12345",
        priority=Priority.HIGH,
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["priority"] is True


def test_create_effect_with_normal_priority() -> None:
    """Test creating effect with NORMAL priority succeeds."""
    effect = AssignDocumentReviewer(
        document_id="12345",
        priority=Priority.NORMAL,
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["priority"] is False


def test_create_effect_with_review_required_mode() -> None:
    """Test creating effect with REVIEW_REQUIRED mode succeeds."""
    effect = AssignDocumentReviewer(
        document_id="12345",
        review_mode=ReviewMode.REVIEW_REQUIRED,
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["review_mode"] == "RR"


def test_create_effect_with_already_reviewed_mode() -> None:
    """Test creating effect with ALREADY_REVIEWED mode succeeds."""
    effect = AssignDocumentReviewer(
        document_id="12345",
        review_mode=ReviewMode.ALREADY_REVIEWED,
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["review_mode"] == "AR"


def test_create_effect_with_review_not_required_mode() -> None:
    """Test creating effect with REVIEW_NOT_REQUIRED mode succeeds."""
    effect = AssignDocumentReviewer(
        document_id="12345",
        review_mode=ReviewMode.REVIEW_NOT_REQUIRED,
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["review_mode"] == "RN"


def test_create_effect_with_annotations() -> None:
    """Test creating effect with annotations succeeds."""
    effect = AssignDocumentReviewer(
        document_id="12345",
        reviewer_id="staff-key-123",
        annotations=[
            Annotation(text="Team lead", color="#FF0000"),
            Annotation(text="Primary care", color="#00FF00"),
        ],
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["annotations"] == [
        {"text": "Team lead", "color": "#FF0000"},
        {"text": "Primary care", "color": "#00FF00"},
    ]


def test_create_effect_with_source_protocol() -> None:
    """Test creating effect with source_protocol succeeds."""
    effect = AssignDocumentReviewer(
        document_id="12345",
        reviewer_id="staff-key-123",
        source_protocol="llm_v1",
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["source_protocol"] == "llm_v1"


def test_create_effect_with_all_fields() -> None:
    """Test creating effect with all fields succeeds."""
    effect = AssignDocumentReviewer(
        document_id="12345",
        reviewer_id="staff-key-123",
        team_id="team-uuid-456",
        priority=Priority.HIGH,
        review_mode=ReviewMode.REVIEW_REQUIRED,
        annotations=[
            Annotation(text="Team lead", color="#FF0000"),
            Annotation(text="Primary care", color="#00FF00"),
        ],
        source_protocol="llm_v1",
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["document_id"] == "12345"
    assert payload["data"]["reviewer_id"] == "staff-key-123"
    assert payload["data"]["team_id"] == "team-uuid-456"
    assert payload["data"]["priority"] is True
    assert payload["data"]["review_mode"] == "RR"
    assert payload["data"]["annotations"] == [
        {"text": "Team lead", "color": "#FF0000"},
        {"text": "Primary care", "color": "#00FF00"},
    ]
    assert payload["data"]["source_protocol"] == "llm_v1"


def test_values_property_returns_correct_structure() -> None:
    """Test values property returns correctly structured dict."""
    effect = AssignDocumentReviewer(
        document_id="12345",
        reviewer_id="staff-key-123",
    )

    values = effect.values
    assert values["document_id"] == "12345"
    assert values["reviewer_id"] == "staff-key-123"
    assert values["priority"] is False
    assert values["review_mode"] == "RR"


def test_values_strips_whitespace_from_document_id() -> None:
    """Test values property strips whitespace from document_id."""
    effect = AssignDocumentReviewer(document_id="  12345  ")
    assert effect.values["document_id"] == "12345"


def test_values_strips_whitespace_from_reviewer_id() -> None:
    """Test values property strips whitespace from reviewer_id."""
    effect = AssignDocumentReviewer(
        document_id="12345",
        reviewer_id="  staff-key  ",
    )
    assert effect.values["reviewer_id"] == "staff-key"


def test_values_strips_whitespace_from_team_id() -> None:
    """Test values property strips whitespace from team_id."""
    effect = AssignDocumentReviewer(
        document_id="12345",
        team_id="  team-uuid  ",
    )
    assert effect.values["team_id"] == "team-uuid"


def test_values_strips_whitespace_from_source_protocol() -> None:
    """Test values property strips whitespace from source_protocol."""
    effect = AssignDocumentReviewer(
        document_id="12345",
        source_protocol="  llm_v1  ",
    )
    assert effect.values["source_protocol"] == "llm_v1"


def test_values_excludes_none_optional_fields() -> None:
    """Test values property excludes None optional fields."""
    effect = AssignDocumentReviewer(document_id="12345")

    values = effect.values
    assert "reviewer_id" not in values
    assert "team_id" not in values
    assert "annotations" not in values
    assert "source_protocol" not in values


def test_values_includes_empty_annotations_list() -> None:
    """Test values property includes empty annotations list when set."""
    effect = AssignDocumentReviewer(
        document_id="12345",
        annotations=[],
    )
    assert effect.values["annotations"] == []


def test_annotations_with_single_item() -> None:
    """Test annotations with a single item."""
    effect = AssignDocumentReviewer(
        document_id="12345",
        annotations=[Annotation(text="Team lead", color="#FF0000")],
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["annotations"] == [{"text": "Team lead", "color": "#FF0000"}]


def test_annotations_with_multiple_items() -> None:
    """Test annotations with multiple items."""
    effect = AssignDocumentReviewer(
        document_id="12345",
        annotations=[
            Annotation(text="Team lead", color="#FF0000"),
            Annotation(text="Primary care", color="#00FF00"),
            Annotation(text="High priority", color="#0000FF"),
        ],
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["annotations"] == [
        {"text": "Team lead", "color": "#FF0000"},
        {"text": "Primary care", "color": "#00FF00"},
        {"text": "High priority", "color": "#0000FF"},
    ]


def test_annotations_preserves_order() -> None:
    """Test annotations preserves the order of items."""
    annotations = [
        Annotation(text="First", color="#111111"),
        Annotation(text="Second", color="#222222"),
        Annotation(text="Third", color="#333333"),
    ]
    effect = AssignDocumentReviewer(
        document_id="12345",
        annotations=annotations,
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["annotations"] == [
        {"text": "First", "color": "#111111"},
        {"text": "Second", "color": "#222222"},
        {"text": "Third", "color": "#333333"},
    ]


def test_annotations_not_included_when_none() -> None:
    """Test annotations is not included when None."""
    effect = AssignDocumentReviewer(document_id="12345")
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert "annotations" not in payload["data"]


def test_source_protocol_included_in_payload() -> None:
    """Test source_protocol is included in payload."""
    effect = AssignDocumentReviewer(
        document_id="12345",
        source_protocol="llm_v1",
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["source_protocol"] == "llm_v1"


def test_source_protocol_not_included_when_none() -> None:
    """Test source_protocol is not included when None."""
    effect = AssignDocumentReviewer(document_id="12345")
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert "source_protocol" not in payload["data"]


def test_source_protocol_empty_string_is_stripped() -> None:
    """Test source_protocol empty string with whitespace is stripped."""
    effect = AssignDocumentReviewer(
        document_id="12345",
        source_protocol="   ",
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["source_protocol"] == ""


def test_apply_without_document_id_raises_error() -> None:
    """Test that apply() without document_id raises ValidationError."""
    effect = AssignDocumentReviewer()

    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    assert "document_id" in str(exc_info.value)


def test_apply_with_none_document_id_raises_error() -> None:
    """Test that apply() with None document_id raises ValidationError."""
    effect = AssignDocumentReviewer(document_id=None)

    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    assert "document_id" in str(exc_info.value)


def test_priority_normal_value() -> None:
    """Test Priority.NORMAL has correct value."""
    assert Priority.NORMAL.value == "normal"


def test_priority_high_value() -> None:
    """Test Priority.HIGH has correct value."""
    assert Priority.HIGH.value == "high"


def test_review_mode_review_required_value() -> None:
    """Test ReviewMode.REVIEW_REQUIRED has correct value."""
    assert ReviewMode.REVIEW_REQUIRED.value == "review_required"


def test_review_mode_already_reviewed_value() -> None:
    """Test ReviewMode.ALREADY_REVIEWED has correct value."""
    assert ReviewMode.ALREADY_REVIEWED.value == "already_reviewed"


def test_review_mode_review_not_required_value() -> None:
    """Test ReviewMode.REVIEW_NOT_REQUIRED has correct value."""
    assert ReviewMode.REVIEW_NOT_REQUIRED.value == "review_not_required"
