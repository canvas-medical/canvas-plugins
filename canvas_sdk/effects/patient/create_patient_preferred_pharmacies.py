import json
from typing import Any
from uuid import UUID

from canvas_generated.messages.effects_pb2 import Effect
from canvas_sdk.effects import _BaseEffect
from canvas_sdk.effects.patient import PatientPreferredPharmacy


class CreatePatientPreferredPharmacies(_BaseEffect):
    """Effect to create a Patient External Identifier record."""

    class Meta:
        effect_type = "CREATE_PATIENT_PREFERRED_PHARMACIES"

    pharmacies: list[PatientPreferredPharmacy]
    patient_id: str | UUID

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
