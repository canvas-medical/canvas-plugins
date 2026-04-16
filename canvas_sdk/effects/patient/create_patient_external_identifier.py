import json

from pydantic import NonNegativeInt

from canvas_generated.messages.effects_pb2 import Effect
from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.effects.base import validate_delay_seconds


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

    @validate_delay_seconds
    def create(self, delay_seconds: NonNegativeInt | None = None) -> Effect:
        """Create a new Patient External Identifier."""
        self._validate_before_effect("create")

        effect = Effect(
            type=f"CREATE_{self.Meta.effect_type}",
            payload=json.dumps(
                {
                    "data": self.values,
                }
            ),
        )
        if delay_seconds is not None:
            effect.delay_seconds = delay_seconds
        return effect


__exports__ = ("CreatePatientExternalIdentifier",)
