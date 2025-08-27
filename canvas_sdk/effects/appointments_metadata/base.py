import json

from canvas_generated.messages.effects_pb2 import Effect
from canvas_sdk.base import TrackableFieldsModel


class AppointmentsMetadata(TrackableFieldsModel):
    """Effect to upsert an Appointment Metadata record."""

    class Meta:
        effect_type = "APPOINTMENTS_METADATA"

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


__exports__ = ("AppointmentsMetadata",)
