import json

from canvas_generated.messages.effects_pb2 import Effect
from canvas_sdk.base import TrackableFieldsModel


class CreatePatientExternalIdentifier(TrackableFieldsModel):
    """Effect to create a Patient External Identifier record."""

    class Meta:
        effect_type = "PATIENT_EXTERNAL_IDENTIFIER"

    value: str
    system: str | None = None
    patient_id: str | None = None

    @property
    def values(self) -> dict[str, str | None]:
        """Return the values of the external identifier."""
        return {
            "value": self.value,
            "system": self.system,
            "patient_id": self.patient_id,
        }

    def create(self) -> Effect:
        """Create a new Patient External Identifier."""
        self._validate_before_effect("create")

        return Effect(
            type=f"CREATE_{self.Meta.effect_type}",
            payload=json.dumps(
                {
                    "data": self.values,
                }
            ),
        )


__exports__ = ("CreatePatientExternalIdentifier",)
