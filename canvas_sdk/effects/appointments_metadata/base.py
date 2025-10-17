from typing import Any

from canvas_sdk.effects.metadata import BaseMetadata
from canvas_sdk.v1.data import Appointment


class AppointmentsMetadata(BaseMetadata):
    """Effect to upsert an Appointment Metadata record."""

    class Meta:
        effect_type = "APPOINTMENT_METADATA"

    appointment_id: str

    def _get_error_details(self, method: Any) -> list:
        errors = super()._get_error_details(method)

        if not Appointment.objects.filter(id=self.appointment_id).exists():
            errors.append(
                self._create_error_detail(
                    "appointment_id",
                    f"Appointment with id: {self.appointment_id} does not exist.",
                    self.appointment_id,
                )
            )

        return errors


__exports__ = ("AppointmentsMetadata",)
