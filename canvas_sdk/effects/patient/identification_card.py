import json
from typing import Any

from pydantic import ConfigDict, Field
from pydantic_core import InitErrorDetails

from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.effects import Effect
from canvas_sdk.effects._field_errors import (
    blank_field_errors,
    existing_record_errors,
    upload_key_errors,
)
from canvas_sdk.v1.data.patient import Patient
from canvas_sdk.v1.data.patient import (
    PatientIdentificationCard as PatientIdentificationCardModel,
)

WRITABLE_FIELDS: tuple[str, ...] = ("image_upload_key", "title", "active")


class PatientIdentificationCard(TrackableFieldsModel):
    """
    Effect to create, update, or delete a patient's identification card.

    The card image (PNG or JPEG) is attached by passing the ``key`` of a ``StoredFilePart``
    received on a SimpleAPI route declared with ``file_uploads="stored"``. Canvas copies the
    file into the card, then deletes the upload, so a key can be attached once.

    Existing cards are identified by ``card_id``, the card's ``dbid``.

    Example (create):
        PatientIdentificationCard(
            patient_id="patient-id", image_upload_key=part.key, title="Driver license"
        ).create()

    Example (deactivate):
        PatientIdentificationCard(card_id=card.dbid, active=False).update()
    """

    model_config = ConfigDict(extra="forbid")

    class Meta:
        effect_type = "PATIENT_IDENTIFICATION_CARD"
        create_required_fields = ("patient_id", "image_upload_key")

    card_id: int | None = None
    patient_id: str | None = None
    image_upload_key: str | None = None
    title: str | None = Field(default=None, max_length=255)
    active: bool | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        records = PatientIdentificationCardModel.objects

        if method == "create":
            if self.card_id is not None:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Field 'card_id' should not be set when creating an identification card.",
                        self.card_id,
                    )
                )
            errors.extend(existing_record_errors(self, "patient_id", Patient.objects, "patient"))

        elif method == "update":
            errors.extend(
                existing_record_errors(
                    self,
                    "card_id",
                    records,
                    "identification card",
                    method,
                )
            )
            if self.is_dirty("patient_id"):
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Field 'patient_id' cannot be changed on an existing identification card.",
                        self.patient_id,
                    )
                )

        elif method == "delete":
            errors.extend(
                existing_record_errors(
                    self,
                    "card_id",
                    records,
                    "identification card",
                    method,
                )
            )

        if method in ("create", "update"):
            errors.extend(blank_field_errors(self, ("active",)))
            errors.extend(upload_key_errors(self, "image_upload_key"))

        return errors

    def create(self) -> Effect:
        """Create a new identification card."""
        self._validate_before_effect("create")
        data = {"patient_id": self.patient_id, **self.values_for(WRITABLE_FIELDS)}
        return Effect(type=f"CREATE_{self.Meta.effect_type}", payload=json.dumps({"data": data}))

    def update(self) -> Effect:
        """Update an existing identification card, changing only the fields that were set."""
        self._validate_before_effect("update")
        data = {"card_id": self.card_id, **self.values_for(WRITABLE_FIELDS)}
        return Effect(type=f"UPDATE_{self.Meta.effect_type}", payload=json.dumps({"data": data}))

    def delete(self) -> Effect:
        """Delete an existing identification card."""
        self._validate_before_effect("delete")
        data = {"card_id": self.card_id}
        return Effect(type=f"DELETE_{self.Meta.effect_type}", payload=json.dumps({"data": data}))


__exports__ = ("PatientIdentificationCard",)
