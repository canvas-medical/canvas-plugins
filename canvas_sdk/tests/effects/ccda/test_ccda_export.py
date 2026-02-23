import json
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.ccda import CreateCCDA, DocumentType

SAMPLE_XML_CONTENT = """<?xml version="1.0" encoding="UTF-8"?>
<ClinicalDocument xmlns="urn:hl7-org:v3">
    <typeId root="2.16.840.1.113883.1.3" extension="POCD_HD000040"/>
</ClinicalDocument>"""

INVALID_XML_CONTENT = """<ClinicalDocument>
    <unclosed_tag>
</ClinicalDocument>"""


@pytest.fixture
def mock_patient_exists() -> Generator[MagicMock]:
    """Mock Patient.objects to return that the patient exists."""
    with patch("canvas_sdk.effects.ccda.ccda_export.Patient.objects") as mock_patient:
        mock_patient.filter.return_value.exists.return_value = True
        yield mock_patient


def test_values_with_all_fields() -> None:
    """Test that values property returns all fields correctly."""
    effect = CreateCCDA(
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
    effect = CreateCCDA(
        patient_id="patient-key-123",
        content=SAMPLE_XML_CONTENT,
    )

    assert effect.values == {
        "patient_id": "patient-key-123",
        "content": SAMPLE_XML_CONTENT,
        "document_type": "CCD",
    }


def test_values_with_referral_document_type() -> None:
    """Test that values property works with Referral document type."""
    effect = CreateCCDA(
        patient_id="patient-key-123",
        content=SAMPLE_XML_CONTENT,
        document_type=DocumentType.REFERRAL,
    )

    assert effect.values["document_type"] == "Referral"


def test_document_type_accepts_string_value() -> None:
    """Test that document_type accepts plain strings via strict=False."""
    effect = CreateCCDA(
        patient_id="patient-key-123",
        content=SAMPLE_XML_CONTENT,
        document_type="Referral",  # type: ignore[arg-type]
    )

    assert effect.document_type == DocumentType.REFERRAL
    assert effect.values["document_type"] == "Referral"


def test_effect_payload_structure() -> None:
    """Test that effect_payload has correct structure."""
    effect = CreateCCDA(
        patient_id="patient-key-123",
        content=SAMPLE_XML_CONTENT,
        document_type=DocumentType.CCD,
    )

    payload = effect.effect_payload
    assert "data" in payload
    assert payload["data"]["patient_id"] == "patient-key-123"
    assert payload["data"]["content"] == SAMPLE_XML_CONTENT
    assert payload["data"]["document_type"] == "CCD"


def test_construction_raises_error_without_patient_id() -> None:
    """Test that construction raises validation error when patient_id is missing."""
    with pytest.raises(ValidationError) as exc_info:
        CreateCCDA(content=SAMPLE_XML_CONTENT)  # type: ignore[call-arg]

    assert "patient_id" in str(exc_info.value)


def test_construction_raises_error_with_empty_patient_id() -> None:
    """Test that construction raises validation error when patient_id is empty."""
    with pytest.raises(ValidationError) as exc_info:
        CreateCCDA(patient_id="", content=SAMPLE_XML_CONTENT)

    assert "patient_id" in str(exc_info.value)


def test_construction_raises_error_without_content() -> None:
    """Test that construction raises validation error when content is missing."""
    with pytest.raises(ValidationError) as exc_info:
        CreateCCDA(patient_id="patient-key-123")  # type: ignore[call-arg]

    assert "content" in str(exc_info.value)


def test_construction_raises_error_with_empty_content() -> None:
    """Test that construction raises validation error when content is empty."""
    with pytest.raises(ValidationError) as exc_info:
        CreateCCDA(patient_id="patient-key-123", content="")

    assert "content" in str(exc_info.value)


def test_default_document_type_is_ccd() -> None:
    """Test that document_type defaults to CCD."""
    effect = CreateCCDA(patient_id="patient-key-123", content=SAMPLE_XML_CONTENT)
    assert effect.document_type == DocumentType.CCD


def test_effect_payload_serialization() -> None:
    """Test that effect_payload contains correctly serialized data."""
    effect = CreateCCDA(
        patient_id="test-patient-key",
        content=SAMPLE_XML_CONTENT,
        document_type=DocumentType.REFERRAL,
    )

    payload = effect.effect_payload
    assert payload["data"]["patient_id"] == "test-patient-key"
    assert payload["data"]["content"] == SAMPLE_XML_CONTENT
    assert payload["data"]["document_type"] == "Referral"


def test_document_type_enum_values() -> None:
    """Test DocumentType enum has expected values."""
    assert DocumentType.CCD.value == "CCD"
    assert DocumentType.REFERRAL.value == "Referral"


def test_apply_succeeds_with_valid_data(mock_patient_exists: MagicMock) -> None:
    """Test that apply returns an Effect with correct type and payload."""
    effect = CreateCCDA(
        patient_id="patient-key-123",
        content=SAMPLE_XML_CONTENT,
        document_type=DocumentType.CCD,
    )

    applied = effect.apply()

    assert applied.type == EffectType.CREATE_CCDA
    payload = json.loads(applied.payload)
    assert payload["data"]["patient_id"] == "patient-key-123"
    assert payload["data"]["content"] == SAMPLE_XML_CONTENT
    assert payload["data"]["document_type"] == "CCD"


def test_apply_raises_error_for_nonexistent_patient() -> None:
    """Test that apply raises validation error when patient does not exist."""
    with patch("canvas_sdk.effects.ccda.ccda_export.Patient.objects") as mock_patient:
        mock_patient.filter.return_value.exists.return_value = False

        effect = CreateCCDA(
            patient_id="nonexistent-patient",
            content=SAMPLE_XML_CONTENT,
        )

        with pytest.raises(ValidationError) as exc_info:
            effect.apply()

        assert "does not exist" in str(exc_info.value)


def test_apply_raises_error_for_invalid_xml(mock_patient_exists: MagicMock) -> None:
    """Test that apply raises validation error when content is invalid XML."""
    effect = CreateCCDA(
        patient_id="patient-key-123",
        content=INVALID_XML_CONTENT,
    )

    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    assert "Invalid XML content" in str(exc_info.value)
