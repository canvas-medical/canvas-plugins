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

    # A set to track which fields have been modified.
    _dirty_keys: set[str] = set()

    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)
        self._dirty_keys = set()
        self._dirty_keys.update(data.keys())

    def __setattr__(self, name: str, value: Any) -> None:
        """Set an attribute and mark it as dirty unless excluded."""
        if not name.startswith("_"):
            self._dirty_keys.add(name)
        super().__setattr__(name, value)

    def is_dirty(self, key: str) -> bool:
        """Returns True if the given property has been modified (i.e. marked as dirty), False otherwise."""
        return key in self._dirty_keys

    user_dbid: int
    email: str | None = None
    phone_number: str | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The user's values."""
        result = {}

        for key in self._dirty_keys:
            result[key] = getattr(self, key)

        result["dbid"] = self.user_dbid
        return result

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


__exports__ = ("UpdateUserEffect",)
