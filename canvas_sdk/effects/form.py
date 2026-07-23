from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from pydantic_core import InitErrorDetails

from canvas_sdk.effects import _BaseEffect


class InputType(StrEnum):
    """Type of input for a form field.

    The first three values (text / select / date) are the legacy minimum.
    The remaining values are the widget primitives the Notion gap analysis
    flagged for the Instance Configuration UI — none of these existed in
    the SDK before. Adding them here lets a SettingsPageHandler render the
    same widgets home-app uses in `/set-up/` without rolling its own UI.
    """

    TEXT = "text"
    SELECT = "select"
    DATE = "date"

    # Instance Configuration widget primitives
    CHECKLIST_PICKER = "checklist_picker"
    TOGGLE_CARDS = "toggle_cards"
    COLOR_PICKER = "color_picker"
    GRADIENT_BUILDER = "gradient_builder"
    ICON_PICKER = "icon_picker"
    ADDRESS_LIST = "address_list"
    INLINE_TABLE = "inline_table"
    STATUS_BADGE = "status_badge"
    KEY_PILL = "key_pill"
    BOOLEAN = "boolean"
    NUMBER = "number"
    EMAIL = "email"
    PHONE = "phone"
    URL = "url"
    FILE = "file"
    TEXTAREA = "textarea"


# Widget types that accept the `options` list (label/value pairs that drive
# a choice surface). Other widgets must leave `options` empty.
_OPTION_BEARING_TYPES = frozenset(
    {
        InputType.SELECT,
        InputType.CHECKLIST_PICKER,
        InputType.TOGGLE_CARDS,
        InputType.ICON_PICKER,
    }
)


@dataclass
class FormField:
    """A class representing a form field.

    Beyond the legacy `key/label/required/editable/type/options/value`
    surface, the new widget primitives may need richer config:

    - `help_text`: subtext rendered below the field
    - `group`: section divider key (e.g. "Identity", "Billing Information")
    - `placeholder`: placeholder for text-like widgets
    - `min_value` / `max_value`: bounds for number / date
    - `widget_config`: free-form dict for widget-specific knobs (e.g. an
      INLINE_TABLE's column descriptors, an ADDRESS_LIST's allowed `use`
      tags, a COLOR_PICKER's preset swatches). The home-app renderer reads
      keys it cares about and ignores the rest, so plugins can experiment
      without an SDK round-trip.
    """

    key: str | None = None
    label: str | None = None
    required: bool = False
    editable: bool = True
    type: InputType = InputType.TEXT
    options: list[str] | None = None
    value: Any | None = None
    help_text: str | None = None
    group: str | None = None
    placeholder: str | None = None
    min_value: Any | None = None
    max_value: Any | None = None
    widget_config: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert the Field to a dictionary.

        Extended widget-config fields are emitted only when set so the
        legacy minimal field shape (`key/label/required/editable/type/
        options/value`) is preserved for callers that haven't opted in.
        """
        out: dict[str, Any] = {
            "key": self.key,
            "label": self.label,
            "required": self.required,
            "editable": self.editable,
            "type": self.type.value,
            "options": self.options,
            "value": self.value,
        }
        if self.help_text is not None:
            out["help_text"] = self.help_text
        if self.group is not None:
            out["group"] = self.group
        if self.placeholder is not None:
            out["placeholder"] = self.placeholder
        if self.min_value is not None:
            out["min_value"] = self.min_value
        if self.max_value is not None:
            out["max_value"] = self.max_value
        if self.widget_config:
            out["widget_config"] = self.widget_config
        return out


class BaseCreateFormEffect(_BaseEffect):
    """Base class for form creation effects."""

    form_fields: list[FormField]

    @property
    def values(self) -> dict[str, Any]:
        """Return the values of the form as a dictionary."""
        return {"form": [form_field.to_dict() for form_field in self.form_fields]}

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        for form_field in self.form_fields:
            if form_field.options and form_field.type not in _OPTION_BEARING_TYPES:
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"The options attribute is only used for fields of type {sorted(t.value for t in _OPTION_BEARING_TYPES)}",
                        form_field.key,
                    )
                )

        return errors


__exports__ = ("FormField", "InputType", "BaseCreateFormEffect")
