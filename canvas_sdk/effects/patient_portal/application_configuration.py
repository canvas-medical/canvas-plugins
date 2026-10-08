from typing import Any

from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect
from canvas_sdk.v1.data import Application


class PatientPortalApplicationConfiguration(_BaseEffect):
    """An effect to configure patient portal application."""

    class Meta:
        effect_type = EffectType.PATIENT_PORTAL__APPLICATION_CONFIGURATION

    can_schedule_appointments: bool | None = None
    default_homepage_application_identifier: str | None = None

    @property
    def values(self) -> dict[str, Any]:
        """Application Configuration values."""
        return {
            "can_schedule_appointments": self.can_schedule_appointments,
            "default_homepage_application_identifier": self.default_homepage_application_identifier,
        }

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"data": self.values}

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if (
            self.default_homepage_application_identifier
            and not Application.objects.filter(
                identifier=self.default_homepage_application_identifier
            ).exists()
        ):
            errors.append(
                self._create_error_detail(
                    "default_homepage_application_identifier",
                    f"Application with identifier {self.default_homepage_application_identifier} does not exist",
                    self.default_homepage_application_identifier,
                )
            )

        return errors


__exports__ = ("PatientPortalApplicationConfiguration",)
