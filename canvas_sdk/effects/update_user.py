from typing import Any

from canvas_sdk.effects.base import EffectType, _BaseEffect


class UpdateUserEffect(_BaseEffect):
    """
    An Effect that will update the user properties.
    """

    class Meta:
        effect_type = EffectType.UPDATE_USER

    dbid: int
    email: str | None = None
    phone_number: str | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The user's values."""
        return {"dbid": self.dbid, "email": self.email, "phone_number": self.phone_number}

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"data": self.values}
