from typing import Any

from pydantic_core import InitErrorDetails

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.form import BaseCreateFormEffect, FormField, InputType  # noqa


class CommandMetadataCreateFormEffect(BaseCreateFormEffect):
    """An Effect that declares additional fields to render on a command."""

    command_uuid: str

    class Meta:
        effect_type = EffectType.COMMAND__FORM__CREATE_ADDITIONAL_FIELDS

    @property
    def values(self) -> dict[str, Any]:
        """Return the command uuid and form fields."""
        return {
            "command": self.command_uuid,
            "form": [field.to_dict() for field in self.form_fields],
        }

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        seen_keys: set[str] = set()
        duplicate_keys: set[str] = set()
        for field in self.form_fields:
            if field.key is None:
                continue
            if field.key in seen_keys:
                duplicate_keys.add(field.key)
            else:
                seen_keys.add(field.key)

        for duplicate_key in duplicate_keys:
            errors.append(
                self._create_error_detail(
                    "form_fields",
                    f"Duplicate form field key: {duplicate_key!r}",
                    duplicate_key,
                )
            )

        return errors


__exports__ = ("CommandMetadataCreateFormEffect", "FormField", "InputType")
