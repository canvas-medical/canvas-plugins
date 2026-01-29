import pytest
from pydantic import ValidationError

from canvas_sdk.effects.ccda import CreateCCDAExport, DocumentType

SAMPLE_XML_CONTENT = """<?xml version="1.0" encoding="UTF-8"?>
<ClinicalDocument xmlns="urn:hl7-org:v3">
    <typeId root="2.16.840.1.113883.1.3" extension="POCD_HD000040"/>
</ClinicalDocument>"""

INVALID_XML_CONTENT = """<ClinicalDocument>
    <unclosed_tag>
</ClinicalDocument>"""


def test_values_with_all_fields() -> None:
    """Test that values property returns all fields correctly."""
    effect = CreateCCDAExport(
        patient_id="patient-key-123",
        content=SAMPLE_XML_CONTENT,
        document_type=DocumentType.CCD,
    )

    assert effect.values == {
        "patient_id": "patient-key-123",
        "content": SAMPLE_XML_CONTENT,
        "document_type": "CCD",
    }


def test_values_with_minimal_fields() -> None:
    """Test that values property returns correctly with required fields and default document_type."""
    effect = CreateCCDAExport(
        patient_id="patient-key-123",
        content=SAMPLE_XML_CONTENT,
    )

    assert effect.values == {
        "patient_id": "patient-key-123",
        "content": SAMPLE_XML_CONTENT,
        "document_type": "CCD",  # default
    }


def test_values_with_referral_document_type() -> None:
    """Test that values property works with Referral document type."""
    effect = CreateCCDAExport(
        patient_id="patient-key-123",
        content=SAMPLE_XML_CONTENT,
        document_type=DocumentType.REFERRAL,
    )

    assert effect.values["document_type"] == "Referral"


def test_effect_payload_structure() -> None:
    """Test that effect_payload has correct structure."""
    effect = CreateCCDAExport(
        patient_id="patient-key-123",
        content=SAMPLE_XML_CONTENT,
        document_type=DocumentType.CCD,
    )

    payload = effect.effect_payload
    assert "data" in payload
    assert payload["data"]["patient_id"] == "patient-key-123"
    assert payload["data"]["content"] == SAMPLE_XML_CONTENT
    assert payload["data"]["document_type"] == "CCD"


def test_apply_raises_error_without_patient_id() -> None:
    """Test that apply raises validation error when patient_id is missing."""
    with pytest.raises(ValidationError) as exc_info:
        CreateCCDAExport(content=SAMPLE_XML_CONTENT)  # type: ignore[call-arg]

    assert "patient_id" in str(exc_info.value)


def test_apply_raises_error_with_empty_patient_id() -> None:
    """Test that apply raises validation error when patient_id is empty."""
    with pytest.raises(ValidationError) as exc_info:
        CreateCCDAExport(patient_id="", content=SAMPLE_XML_CONTENT)

    assert "patient_id" in str(exc_info.value)


def test_apply_raises_error_without_content() -> None:
    """Test that apply raises validation error when content is missing."""
    with pytest.raises(ValidationError) as exc_info:
        CreateCCDAExport(patient_id="patient-key-123")  # type: ignore[call-arg]

    assert "content" in str(exc_info.value)


def test_apply_raises_error_with_empty_content() -> None:
    """Test that apply raises validation error when content is empty."""
    with pytest.raises(ValidationError) as exc_info:
        CreateCCDAExport(patient_id="patient-key-123", content="")

    assert "content" in str(exc_info.value)


def test_default_document_type_is_ccd() -> None:
    """Test that document_type defaults to CCD."""
    effect = CreateCCDAExport(patient_id="patient-key-123", content=SAMPLE_XML_CONTENT)
    assert effect.document_type == DocumentType.CCD


def test_effect_type_is_create_ccda_export() -> None:
    """Test that the effect type is CREATE_CCDA_EXPORT."""
    from canvas_generated.messages.effects_pb2 import EffectType

    assert CreateCCDAExport.Meta.effect_type == EffectType.CREATE_CCDA_EXPORT


def test_effect_payload_serialization() -> None:
    """Test that effect_payload contains correctly serialized data."""
    effect = CreateCCDAExport(
        patient_id="test-patient-key",
        content=SAMPLE_XML_CONTENT,
        document_type=DocumentType.REFERRAL,
    )

    # Check the payload structure directly (without calling apply which validates patient)
    payload = effect.effect_payload
    assert payload["data"]["patient_id"] == "test-patient-key"
    assert payload["data"]["content"] == SAMPLE_XML_CONTENT
    assert payload["data"]["document_type"] == "Referral"


def test_document_type_enum_values() -> None:
    """Test DocumentType enum has expected values."""
    assert DocumentType.CCD.value == "CCD"
    assert DocumentType.REFERRAL.value == "Referral"


def test_invalid_xml_content_detected() -> None:
    """Test that invalid XML content can be detected by XML parser."""
    import xml.etree.ElementTree as ET

    # Verify that our test invalid XML is actually invalid
    with pytest.raises(ET.ParseError):
        ET.fromstring(INVALID_XML_CONTENT)

    # And that valid XML parses fine
    ET.fromstring(SAMPLE_XML_CONTENT)  # Should not raise
