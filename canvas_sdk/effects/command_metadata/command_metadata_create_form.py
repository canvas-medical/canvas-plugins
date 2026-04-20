from typing import Any

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


__exports__ = ("CommandMetadataCreateFormEffect", "FormField", "InputType")
