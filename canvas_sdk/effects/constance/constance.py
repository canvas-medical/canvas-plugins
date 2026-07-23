import json
from typing import Any

from pydantic_core import InitErrorDetails

from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.effects import Effect


class ConstanceValue(TrackableFieldsModel):
    """
    Effect to set a `django-constance` runtime config value.

    Note: the home-app interpreter validates the key against
    `settings.CONSTANCE_CONFIG` and rejects unknown keys / wrong-typed values.
    """

    class Meta:
        effect_type = "CONSTANCE_VALUE"

    key: str | None = None
    value: Any | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        if method == "set":
            if not self.key:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'key' is required to set a constance value.",
                        self.key,
                    )
                )
            if self.value is None:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'value' is required to set a constance value.",
                        self.value,
                    )
                )
        return errors

    def set(self) -> Effect:
        """Set a django-constance value."""
        self._validate_before_effect("set")
        return Effect(
            type=f"SET_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )


__exports__ = ("ConstanceValue",)
