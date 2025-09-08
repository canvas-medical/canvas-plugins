from typing import Any

from pydantic_core import InitErrorDetails

from canvas_sdk.effects.metadata import BaseMetadata
from canvas_sdk.v1.data import Patient


class PatientMetadata(BaseMetadata):
    """Effect to upsert a Patient Metadata record."""

    class Meta:
        effect_type = "PATIENT_METADATA"

    patient_id: str

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


__exports__ = ("PatientMetadata",)
