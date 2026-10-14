"""Tests for the PatientIdentificationCard effect."""

import json
from typing import Any

import pytest
from pydantic_core import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.patient import PatientIdentificationCard
from canvas_sdk.test_utils.factories import PatientFactory
from canvas_sdk.v1.data import Patient
from canvas_sdk.v1.data.patient import (
    PatientIdentificationCard as PatientIdentificationCardModel,
)

UPLOAD_KEY = "acme/plugin-uploads/my_plugin/20261014T120000Z-abc-license.jpg"


@pytest.fixture
def patient() -> Patient:
    """A patient to attach cards to."""
    return PatientFactory.create()


@pytest.fixture
def card(patient: Patient) -> PatientIdentificationCardModel:
    """An existing identification card."""
    return PatientIdentificationCardModel.objects.create(
        patient=patient, image="identification-cards/license.jpg", title="License"
    )


def _payload(effect: Any) -> dict[str, Any]:
    return json.loads(effect.payload)["data"]


@pytest.mark.django_db
def test_create(patient: Patient) -> None:
    """create() sends the patient, the upload key and the fields that were set."""
    effect = PatientIdentificationCard(
        patient_id=patient.id, image_upload_key=UPLOAD_KEY, title="Driver license"
    ).create()

    assert effect.type == EffectType.CREATE_PATIENT_IDENTIFICATION_CARD
    assert _payload(effect) == {
        "patient_id": patient.id,
        "image_upload_key": UPLOAD_KEY,
        "title": "Driver license",
    }


@pytest.mark.django_db
@pytest.mark.parametrize(
    "kwargs, message",
    [
        ({"image_upload_key": UPLOAD_KEY}, "'patient_id' is required"),
        ({"patient_id": "0" * 32, "image_upload_key": UPLOAD_KEY}, "does not exist"),
        ({"patient_id": "PATIENT"}, "'image_upload_key' is required"),
        ({"patient_id": "PATIENT", "image_upload_key": "license.jpg"}, "image_upload_key"),
        ({"patient_id": "PATIENT", "image_upload_key": UPLOAD_KEY, "card_id": 1}, "card_id"),
    ],
)
def test_create_rejects_invalid_input(
    patient: Patient, kwargs: dict[str, Any], message: str
) -> None:
    """create() needs an existing patient and an upload key, and no card id."""
    if kwargs.get("patient_id") == "PATIENT":
        kwargs = {**kwargs, "patient_id": patient.id}

    with pytest.raises(ValidationError, match=message):
        PatientIdentificationCard(**kwargs).create()


@pytest.mark.django_db
def test_update_sends_only_set_fields(card: PatientIdentificationCardModel) -> None:
    """update() sends the card id and only the fields that were set."""
    effect = PatientIdentificationCard(card_id=card.dbid, active=False).update()

    assert effect.type == EffectType.UPDATE_PATIENT_IDENTIFICATION_CARD
    assert _payload(effect) == {"card_id": card.dbid, "active": False}


@pytest.mark.django_db
@pytest.mark.parametrize("field", ["image_upload_key", "active"])
def test_update_rejects_null_for_required_fields(
    card: PatientIdentificationCardModel, field: str
) -> None:
    """The image and active flag cannot be cleared."""
    with pytest.raises(ValidationError, match=f"Field '{field}' cannot be set to null"):
        PatientIdentificationCard(card_id=card.dbid, **{field: None}).update()


@pytest.mark.django_db
def test_update_rejects_patient_change(card: PatientIdentificationCardModel) -> None:
    """A card cannot move to another patient."""
    with pytest.raises(ValidationError, match="'patient_id' cannot be changed"):
        PatientIdentificationCard(card_id=card.dbid, patient_id="someone").update()


@pytest.mark.django_db
@pytest.mark.parametrize("method", ["update", "delete"])
def test_requires_existing_card(method: str) -> None:
    """update() and delete() need a card id that exists."""
    with pytest.raises(ValidationError, match="'card_id' is required"):
        getattr(PatientIdentificationCard(), method)()
    with pytest.raises(ValidationError, match="does not exist"):
        getattr(PatientIdentificationCard(card_id=999999), method)()


@pytest.mark.django_db
def test_delete(card: PatientIdentificationCardModel) -> None:
    """delete() sends only the card id."""
    effect = PatientIdentificationCard(card_id=card.dbid, title="ignored").delete()

    assert effect.type == EffectType.DELETE_PATIENT_IDENTIFICATION_CARD
    assert _payload(effect) == {"card_id": card.dbid}
