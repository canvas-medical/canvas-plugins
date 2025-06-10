import json
from typing import Any

from pydantic_core import InitErrorDetails

from canvas_generated.messages.effects_pb2 import Effect
from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.v1.data import Patient


class PatientMetadata(TrackableFieldsModel):
    """Effect to upsert a Patient Metadata record."""

    class Meta:
        effect_type = "PATIENT_METADATA"

    patient_id: str
    key: str

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if not Patient.objects.filter(id=self.patient_id).exists():
            errors.append(
                self._create_error_detail(
                    "patient_id",
                    f"Patient with id: {self.patient_id} does not exist.",
                    self.patient_id,
                )
            )

        return errors

    def upsert(self, value: str) -> Effect:
        """Upsert the patient metadata."""
        self._validate_before_effect("upsert")

        return Effect(
            type=f"UPSERT_{self.Meta.effect_type}",
            payload=json.dumps(
                {
                    "data": {**self.values, "value": value},
                }
            ),
        )


__exports__ = ("PatientMetadata",)
