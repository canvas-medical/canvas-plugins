from typing import Any

from pydantic import Field

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.base import _BaseEffect


class SetApplicationNotificationBadge(_BaseEffect):
    """An Effect that sets the notification badge count for an Application icon.

    Targets are specified as two parallel lists:

    - ``staff_ids``: staff keys whose EMR badge should update.
    - ``patient_ids``: patient keys whose portal badge should update.

    Both lists may be combined in a single effect (e.g., a message between a staff
    member and a patient updates both sides at once). When both lists are empty the
    update is broadcast to every connected user.
    """

    class Meta:
        effect_type = EffectType.SET_APPLICATION_NOTIFICATION_BADGE

    application_identifier: str = Field(min_length=1)
    count: int = Field(ge=0)
    staff_ids: list[str] = Field(default_factory=list)
    patient_ids: list[str] = Field(default_factory=list)

    @property
    def values(self) -> dict[str, Any]:
        """The SetApplicationNotificationBadge effect's values."""
        return {
            "application_identifier": self.application_identifier,
            "count": self.count,
            "staff_ids": self.staff_ids,
            "patient_ids": self.patient_ids,
        }

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"data": self.values}


__exports__ = ("SetApplicationNotificationBadge",)
