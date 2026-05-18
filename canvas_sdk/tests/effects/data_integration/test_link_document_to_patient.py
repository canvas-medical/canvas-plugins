import json

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.data_integration import LinkDocumentToPatient
from canvas_sdk.effects.data_integration.types import AnnotationItem


def test_create_effect_with_all_required_fields() -> None:
    """Test creating effect with all required fields succeeds."""
    effect = LinkDocumentToPatient(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        patient_key="patient-key-67890",
    )
    applied = effect.apply()

    assert applied.type == EffectType.LINK_DOCUMENT_TO_PATIENT

    payload = json.loads(applied.payload)
    assert payload["data"] == {
        "document_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "patient_key": "patient-key-67890",
        "annotations": None,
        "source_protocol": None,
    }


def test_create_effect_with_annotations() -> None:
    """Test creating effect with annotations succeeds."""
    effect = LinkDocumentToPatient(
        document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        patient_key="patient-key-67890",
        annotations=[
            AnnotationItem(text="AI 95%", color="#00AA00"),
            AnnotationItem(text="DOB matched", color="#2196F3"),
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
            AnnotationItem(text="AI 95%", color="#00AA00"),
            AnnotationItem(text="DOB matched", color="#2196F3"),
            AnnotationItem(text="Name verified", color="#4CAF50"),
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
        "annotations": None,
        "source_protocol": None,
    }


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
