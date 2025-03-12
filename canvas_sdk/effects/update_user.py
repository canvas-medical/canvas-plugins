from typing import Any, Self

from pydantic import model_validator
from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect
from canvas_sdk.v1.data import CanvasUser


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

    @model_validator(mode="after")
    def check_exclusive_fields(self) -> Self:
        """Check that at least one of mutually exclusive field is set."""
        if self.email is None and self.phone_number is None:
            raise ValueError("one of 'email', 'phone_number' is required")

        return self

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        user = CanvasUser.objects.get(dbid=self.dbid)

        if user is None:
            errors.append(
                self._create_error_detail(
                    "value",
                    "User does not exist",
                    self.dbid,
                )
            )

        return errors
