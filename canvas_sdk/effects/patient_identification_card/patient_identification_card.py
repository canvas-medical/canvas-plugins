"""Plugin effect for creating, updating, or deleting a PatientIdentificationCard.

Card images are attached by passing an S3 key under your plugin's uploads
prefix (``plugin-uploads/<your-plugin-name>/...``) on ``image_upload_key``.
Canvas performs a server-side S3 copy into the canonical
``identification-cards/`` storage when the effect is applied — no file bytes
pass through your plugin.
"""

from __future__ import annotations

import json
from typing import Any

from pydantic_core import InitErrorDetails

from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.effects import Effect
from canvas_sdk.effects._upload_key import check_upload_key
from canvas_sdk.v1.data.patient import (
    Patient,
    PatientIdentificationCard as PatientIdentificationCardModel,
)


class PatientIdentificationCard(TrackableFieldsModel):
    """Effect for creating, updating, or deleting a PatientIdentificationCard.

    Example (create with a freshly uploaded image)::

        effect = PatientIdentificationCard(
            patient_id=patient_key,
            image_upload_key=upload_key,
            title="Driver license",
        )
        return [effect.create()]

    Example (toggle active)::

        effect = PatientIdentificationCard(card_id=card_dbid, active=False)
        return [effect.update()]
    """

    class Meta:
        effect_type = "PATIENT_IDENTIFICATION_CARD"

    # Numeric platform PK for update / delete (matches the SDK Transactor
    # surface — PatientIdentificationCard has no UUID externally_exposable_id
    # field at the SDK layer today, so we use dbid as the stable handle).
    card_id: int | None = None

    # Patient lookup key. Required on create.
    patient_id: str | None = None

    image_upload_key: str | None = None
    title: str | None = None
    active: bool | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if method == "create":
            if self.card_id is not None:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Field 'card_id' must not be set when creating a card.",
                        self.card_id,
                    )
                )
            if not self.patient_id:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'patient_id' is required to create a card.",
                        self.patient_id,
                    )
                )
            elif not Patient.objects.filter(id=self.patient_id).exists():
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Patient with id {self.patient_id!r} does not exist.",
                        self.patient_id,
                    )
                )
            if not self.image_upload_key:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'image_upload_key' is required to create a card.",
                        self.image_upload_key,
                    )
                )

        if method in ("update", "delete"):
            if self.card_id is None:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'card_id' is required to update or delete a card.",
                        self.card_id,
                    )
                )
            elif not PatientIdentificationCardModel.objects.filter(dbid=self.card_id).exists():
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"PatientIdentificationCard with id {self.card_id!r} does not exist.",
                        self.card_id,
                    )
                )

        if method in ("create", "update"):
            err = check_upload_key(
                self.image_upload_key, field_label="ID card image upload key"
            )
            if err:
                errors.append(self._create_error_detail("value", err, self.image_upload_key))

        return errors

    def create(self) -> Effect:
        """Create a new PatientIdentificationCard."""
        self._validate_before_effect("create")
        return Effect(
            type=f"CREATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )

    def update(self) -> Effect:
        """Update an existing PatientIdentificationCard. Only fields you set
        are changed; image_upload_key is processed only when provided."""
        self._validate_before_effect("update")
        return Effect(
            type=f"UPDATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )

    def delete(self) -> Effect:
        """Delete an existing PatientIdentificationCard."""
        self._validate_before_effect("delete")
        return Effect(
            type=f"DELETE_{self.Meta.effect_type}",
            payload=json.dumps({"data": {"card_id": self.card_id}}),
        )


__exports__ = ("PatientIdentificationCard",)
