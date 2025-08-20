import json
from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_generated.messages.effects_pb2 import Effect
from canvas_sdk.effects import _BaseEffect
from canvas_sdk.effects.patient import PatientPreferredPharmacy
from canvas_sdk.v1.data import Patient


class CreatePatientPreferredPharmacies(_BaseEffect):
    """Effect to create a Patient External Identifier record."""

    class Meta:
        effect_type = "CREATE_PATIENT_PREFERRED_PHARMACIES"

    pharmacies: list[PatientPreferredPharmacy]
    patient_id: str | UUID

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if not Patient.objects.filter(id=self.patient_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Patient with ID {self.patient_id} does not exist.",
                    self.patient_id,
                )
            )

        default_count = sum(1 for pharmacy in self.pharmacies if pharmacy.default)
        if default_count > 1:
            errors.append(
                self._create_error_detail(
                    "value",
                    "Only one preferred pharmacy can be set as default.",
                    None,
                )
            )

        return errors

    @property
    def values(self) -> dict[str, Any]:
        """Return the values of the preferred pharmacies."""
        return {
            "preferred_pharmacies": [
                preferred_pharmacy.to_dict() for preferred_pharmacy in self.pharmacies
            ],
            "patient_id": str(self.patient_id),
        }

    def create(self) -> Effect:
        """Create Patient Preferred Pharmacies."""
        self._validate_before_effect("create")

        return Effect(
            type=self.Meta.effect_type,
            payload=json.dumps(
                {
                    "data": self.values,
                }
            ),
        )


__exports__ = ("CreatePatientPreferredPharmacies",)
