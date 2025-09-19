from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect
from canvas_sdk.v1.data import PatientContactPoint


class SendContactVerificationEffect(_BaseEffect):
    """
    An Effect that will send a verification for a Patient Contact Point.
    """

    class Meta:
        effect_type = EffectType.PATIENT_PORTAL__SEND_CONTACT_VERIFICATION

    contact_point_id: str | UUID

    @property
    def values(self) -> dict[str, Any]:
        """The contact point id."""
        return {"contact_point_id": self.contact_point_id}

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        contact_point_exists = PatientContactPoint.objects.filter(id=self.contact_point_id).exists()

        if not contact_point_exists:
            errors.append(
                self._create_error_detail(
                    "value",
                    "Patient Contact Point does not exist",
                    self.contact_point_id,
                )
            )

        return errors


__exports__ = ("SendContactVerificationEffect",)
