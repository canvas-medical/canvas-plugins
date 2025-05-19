from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from canvas_sdk.effects import EffectType, _BaseEffect


class InputType(StrEnum):
    """Type of input for a form field."""

    TEXT = "text"
    SELECT = "select"
    DATE = "date"


@dataclass
class FormField:
    """A class representing a Field."""

    key: str | None = None
    label: str | None = None
    required: bool = False
    editable: bool = True
    type: InputType = InputType.TEXT
    options: list[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the Field to a dictionary."""
        return {
            "key": self.key,
            "label": self.label,
            "required": self.required,
            "editable": self.editable,
            "type": self.type.value,
            "options": self.options,
        }


class CreateFormEffect(_BaseEffect):
    """An Effect that will create a form."""

    class Meta:
        effect_type = EffectType.CREATE_ADDITIONAL_FIELDS

    form_fields: list[FormField]

    @property
    def values(self) -> dict[str, Any]:
        """Return the values of the form as a dictionary."""
        return {"form": [field.to_dict() for field in self.form_fields]}


__exports__ = ("CreateFormEffect", "FormField", "InputType")
