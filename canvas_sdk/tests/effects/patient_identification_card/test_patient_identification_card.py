"""Tests for the PatientIdentificationCard SDK effect."""

from __future__ import annotations

import json
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from pydantic_core import ValidationError

from canvas_sdk.effects.effect import EffectType
from canvas_sdk.effects.patient_identification_card import PatientIdentificationCard

_PATH = "canvas_sdk.effects.patient_identification_card.patient_identification_card"


@pytest.fixture
def mock_db() -> Generator[dict[str, MagicMock], None, None]:
    """Stub Patient/PatientIdentificationCard existence checks to always succeed."""
    with (
        patch(f"{_PATH}.Patient.objects") as mock_patient,
        patch(f"{_PATH}.PatientIdentificationCardModel.objects") as mock_card,
    ):
        mock_patient.filter.return_value.exists.return_value = True
        mock_card.filter.return_value.exists.return_value = True
        yield {"patient": mock_patient, "card": mock_card}


def test_create_emits_create_effect(mock_db: dict[str, MagicMock]) -> None:
    """A valid create() emits CREATE_PATIENT_IDENTIFICATION_CARD with the expected payload."""
    upload_key = "local/plugin-uploads/my_plugin/2026-front.jpg"
    effect = PatientIdentificationCard(
        patient_id="abc-patient",
        image_upload_key=upload_key,
        title="Driver license",
    ).create()
    assert effect.type == EffectType.CREATE_PATIENT_IDENTIFICATION_CARD
    data = json.loads(effect.payload)["data"]
    assert data["patient_id"] == "abc-patient"
    assert data["image_upload_key"] == upload_key
    assert data["title"] == "Driver license"


def test_create_requires_patient_id(mock_db: dict[str, MagicMock]) -> None:
    """create() without a patient_id raises ValidationError."""
    with pytest.raises(ValidationError):
        PatientIdentificationCard(image_upload_key="local/plugin-uploads/my_plugin/x.jpg").create()


def test_create_requires_image_upload_key(mock_db: dict[str, MagicMock]) -> None:
    """create() without an image_upload_key raises ValidationError."""
    with pytest.raises(ValidationError):
        PatientIdentificationCard(patient_id="abc-patient").create()


def test_create_rejects_unknown_patient(mock_db: dict[str, MagicMock]) -> None:
    """create() for a patient that does not exist raises ValidationError."""
    mock_db["patient"].filter.return_value.exists.return_value = False
    with pytest.raises(ValidationError):
        PatientIdentificationCard(
            patient_id="abc-patient",
            image_upload_key="local/plugin-uploads/my_plugin/x.jpg",
        ).create()


def test_create_rejects_bad_upload_key(mock_db: dict[str, MagicMock]) -> None:
    """create() with an upload key outside the plugin-uploads segment raises ValidationError."""
    with pytest.raises(ValidationError):
        PatientIdentificationCard(
            patient_id="abc-patient",
            image_upload_key="not-a-plugin-upload/x.jpg",
        ).create()


def test_create_rejects_card_id(mock_db: dict[str, MagicMock]) -> None:
    """create() rejects a caller-supplied card_id."""
    with pytest.raises(ValidationError):
        PatientIdentificationCard(
            patient_id="abc-patient",
            image_upload_key="local/plugin-uploads/my_plugin/x.jpg",
            card_id=1,
        ).create()


def test_update_emits_update_effect(mock_db: dict[str, MagicMock]) -> None:
    """update() emits UPDATE_PATIENT_IDENTIFICATION_CARD with only the changed fields."""
    effect = PatientIdentificationCard(card_id=42, title="Renewed").update()
    assert effect.type == EffectType.UPDATE_PATIENT_IDENTIFICATION_CARD
    data = json.loads(effect.payload)["data"]
    assert data == {"card_id": 42, "title": "Renewed"}


def test_update_requires_card_id(mock_db: dict[str, MagicMock]) -> None:
    """update() without a card_id raises ValidationError."""
    with pytest.raises(ValidationError):
        PatientIdentificationCard(title="Renewed").update()


def test_update_rejects_unknown_card(mock_db: dict[str, MagicMock]) -> None:
    """update() for a card that does not exist raises ValidationError."""
    mock_db["card"].filter.return_value.exists.return_value = False
    with pytest.raises(ValidationError):
        PatientIdentificationCard(card_id=42, title="x").update()


def test_delete_emits_delete_effect(mock_db: dict[str, MagicMock]) -> None:
    """delete() emits DELETE_PATIENT_IDENTIFICATION_CARD for the given card_id."""
    effect = PatientIdentificationCard(card_id=42).delete()
    assert effect.type == EffectType.DELETE_PATIENT_IDENTIFICATION_CARD
    data = json.loads(effect.payload)["data"]
    assert data == {"card_id": 42}


def test_delete_requires_card_id(mock_db: dict[str, MagicMock]) -> None:
    """delete() without a card_id raises ValidationError."""
    with pytest.raises(ValidationError):
        PatientIdentificationCard().delete()
