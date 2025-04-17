from typing import Any

from canvas_sdk.effects.base import EffectType, _BaseEffect


class PatientPortalApplicationConfiguration(_BaseEffect):
    """An effect to configure patient portal application."""

    class Meta:
        effect_type = EffectType.PATIENT_PORTAL__APPLICATION_CONFIGURATION

    can_schedule_appointments: bool

    @property
    def values(self) -> dict[str, Any]:
        """Application Configuration values."""
        return {"can_schedule_appointments": self.can_schedule_appointments}

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"data": self.values}


__exports__ = ("PatientPortalApplicationConfiguration",)
