import json

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.data_integration import (
    AssignDocumentReviewer,
    Priority,
    ReviewMode,
)
from canvas_sdk.effects.data_integration.types import AnnotationItem


def test_create_effect_with_document_id_only() -> None:
    """Test creating effect with only document_id succeeds."""
    effect = AssignDocumentReviewer(document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890")
    applied = effect.apply()

    assert applied.type == EffectType.ASSIGN_DOCUMENT_REVIEWER

    payload = json.loads(applied.payload)
    assert payload["data"] == {
        "document_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "priority": False,
        "review_mode": "RR",
        "reviewer_id": None,
        "team_id": None,
        "annotations": None,
        "source_protocol": None,
    }


def test_create_effect_with_reviewer_id() -> None:
    """Test creating effect with reviewer_id succeeds."""
    effect = AssignDocumentReviewer(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        reviewer_id="staff-key-123",
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["reviewer_id"] == "staff-key-123"


def test_create_effect_with_team_id() -> None:
    """Test creating effect with team_id succeeds."""
    effect = AssignDocumentReviewer(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        team_id="team-uuid-456",
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["team_id"] == "team-uuid-456"


def test_create_effect_with_both_reviewer_and_team() -> None:
    """Test creating effect with both reviewer_id and team_id succeeds."""
    effect = AssignDocumentReviewer(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        reviewer_id="staff-key-123",
        team_id="team-uuid-456",
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["reviewer_id"] == "staff-key-123"
    assert payload["data"]["team_id"] == "team-uuid-456"


def test_create_effect_with_high_priority() -> None:
    """Test creating effect with HIGH priority succeeds."""
    effect = AssignDocumentReviewer(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        priority=Priority.HIGH,
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["priority"] is True


def test_create_effect_with_normal_priority() -> None:
    """Test creating effect with NORMAL priority succeeds."""
    effect = AssignDocumentReviewer(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        priority=Priority.NORMAL,
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["priority"] is False


def test_create_effect_with_annotations() -> None:
    """Test creating effect with annotations succeeds."""
    effect = AssignDocumentReviewer(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        reviewer_id="staff-key-123",
        annotations=[
            AnnotationItem(text="Team lead", color="#FF0000"),
            AnnotationItem(text="Primary care", color="#00FF00"),
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
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        reviewer_id="staff-key-123",
        source_protocol="llm_v1",
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["source_protocol"] == "llm_v1"


def test_create_effect_with_all_fields() -> None:
    """Test creating effect with all fields succeeds."""
    effect = AssignDocumentReviewer(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        reviewer_id="staff-key-123",
        team_id="team-uuid-456",
        priority=Priority.HIGH,
        review_mode=ReviewMode.REVIEW_REQUIRED,
        annotations=[
            AnnotationItem(text="Team lead", color="#FF0000"),
            AnnotationItem(text="Primary care", color="#00FF00"),
        ],
        source_protocol="llm_v1",
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["document_id"] == "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
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
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        reviewer_id="staff-key-123",
    )

    values = effect.values
    assert values["document_id"] == "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    assert values["reviewer_id"] == "staff-key-123"
    assert values["priority"] is False
    assert values["review_mode"] == "RR"


def test_values_emits_none_for_unset_optional_fields() -> None:
    """Test values property emits None for unset optional fields."""
    effect = AssignDocumentReviewer(document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890")

    assert effect.values == {
        "document_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "priority": False,
        "review_mode": "RR",
        "reviewer_id": None,
        "team_id": None,
        "annotations": None,
        "source_protocol": None,
    }


def test_values_includes_empty_annotations_list() -> None:
    """Test values property includes empty annotations list when set."""
    effect = AssignDocumentReviewer(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        annotations=[],
    )
    assert effect.values["annotations"] == []


def test_annotations_with_single_item() -> None:
    """Test annotations with a single item."""
    effect = AssignDocumentReviewer(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        annotations=[AnnotationItem(text="Team lead", color="#FF0000")],
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["annotations"] == [{"text": "Team lead", "color": "#FF0000"}]


def test_annotations_with_multiple_items() -> None:
    """Test annotations with multiple items."""
    effect = AssignDocumentReviewer(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        annotations=[
            AnnotationItem(text="Team lead", color="#FF0000"),
            AnnotationItem(text="Primary care", color="#00FF00"),
            AnnotationItem(text="High priority", color="#0000FF"),
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
        AnnotationItem(text="First", color="#111111"),
        AnnotationItem(text="Second", color="#222222"),
        AnnotationItem(text="Third", color="#333333"),
    ]
    effect = AssignDocumentReviewer(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        annotations=annotations,
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["annotations"] == [
        {"text": "First", "color": "#111111"},
        {"text": "Second", "color": "#222222"},
        {"text": "Third", "color": "#333333"},
    ]


def test_annotations_none_when_not_provided() -> None:
    """Test annotations is None in payload when not provided."""
    effect = AssignDocumentReviewer(document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890")
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["annotations"] is None


def test_source_protocol_included_in_payload() -> None:
    """Test source_protocol is included in payload."""
    effect = AssignDocumentReviewer(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        source_protocol="llm_v1",
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["source_protocol"] == "llm_v1"


def test_source_protocol_none_when_not_provided() -> None:
    """Test source_protocol is None in payload when not provided."""
    effect = AssignDocumentReviewer(document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890")
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload["data"]["source_protocol"] is None
