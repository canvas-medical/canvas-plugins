import json
from typing import Any

from pydantic_core import InitErrorDetails

from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.effects import Effect
from canvas_sdk.effects._upload_key import is_plugin_upload_key, upload_key_error
from canvas_sdk.v1.data.patient import Patient
from canvas_sdk.v1.data.patient import (
    PatientIdentificationCard as PatientIdentificationCardModel,
)


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

    class Meta:
        effect_type = "PATIENT_IDENTIFICATION_CARD"

    card_id: int | None = None
    patient_id: str | None = None
    image_upload_key: str | None = None
    title: str | None = None
    active: bool | None = None

    def _card_id_errors(self, method: str) -> list[InitErrorDetails]:
        if self.card_id is None:
            return [
                self._create_error_detail(
                    "missing",
                    f"Field 'card_id' is required to {method} an identification card.",
                    None,
                )
            ]
        if not PatientIdentificationCardModel.objects.filter(dbid=self.card_id).exists():
            return [
                self._create_error_detail(
                    "value",
                    f"Identification card with id: {self.card_id} does not exist.",
                    self.card_id,
                )
            ]
        return []

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if method == "create":
            if self.card_id is not None:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Field 'card_id' should not be set when creating an identification card.",
                        self.card_id,
                    )
                )
            if not self.patient_id:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'patient_id' is required to create an identification card.",
                        None,
                    )
                )
            elif not Patient.objects.filter(id=self.patient_id).exists():
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Patient with id: {self.patient_id} does not exist.",
                        self.patient_id,
                    )
                )
            if not self.image_upload_key:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'image_upload_key' is required to create an identification card.",
                        None,
                    )
                )

        elif method == "update":
            errors.extend(self._card_id_errors("update"))
            if self.is_dirty("patient_id"):
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Field 'patient_id' cannot be changed on an existing identification card.",
                        self.patient_id,
                    )
                )
            for field in ("image_upload_key", "active"):
                if self.is_dirty(field) and getattr(self, field) is None:
                    errors.append(
                        self._create_error_detail(
                            "value",
                            f"Field '{field}' cannot be set to null when updating an "
                            "identification card.",
                            None,
                        )
                    )

        elif method == "delete":
            errors.extend(self._card_id_errors("delete"))

        if (
            method in ("create", "update")
            and self.image_upload_key is not None
            and not is_plugin_upload_key(self.image_upload_key)
        ):
            errors.append(
                self._create_error_detail(
                    "value", upload_key_error("image_upload_key"), self.image_upload_key
                )
            )

        return errors

    def _data(self, fields: tuple[str, ...]) -> dict[str, Any]:
        return {field: getattr(self, field) for field in fields if self.is_dirty(field)}

    def create(self) -> Effect:
        """Create a new identification card."""
        self._validate_before_effect("create")
        data = self._data(("patient_id", "image_upload_key", "title", "active"))
        return Effect(
            type=f"CREATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": data}),
        )

    def update(self) -> Effect:
        """Update an existing identification card, changing only the fields that were set."""
        self._validate_before_effect("update")
        data = {"card_id": self.card_id, **self._data(("image_upload_key", "title", "active"))}
        return Effect(
            type=f"UPDATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": data}),
        )

    def delete(self) -> Effect:
        """Delete an existing identification card."""
        self._validate_before_effect("delete")
        return Effect(
            type=f"DELETE_{self.Meta.effect_type}",
            payload=json.dumps({"data": {"card_id": self.card_id}}),
        )


__exports__ = ("PatientIdentificationCard",)
