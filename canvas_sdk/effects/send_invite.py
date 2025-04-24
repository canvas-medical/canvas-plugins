from typing import Any

from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect
from canvas_sdk.v1.data import CanvasUser


class SendInviteEffect(_BaseEffect):
    """
    An Effect that will send an invitation for the Patient Portal.
    """

    class Meta:
        effect_type = EffectType.PATIENT_PORTAL__SEND_INVITE

    user_dbid: int

    @property
    def values(self) -> dict[str, Any]:
        """The user's id."""
        return {"user_dbid": self.user_dbid}

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"data": self.values}

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        user_exists = CanvasUser.objects.filter(dbid=self.user_dbid).exists()

        if not user_exists:
            errors.append(
                self._create_error_detail(
                    "value",
                    "User does not exist",
                    self.user_dbid,
                )
            )

        return errors


__exports__ = ("SendInviteEffect",)
