"""Settings page form effect.

Returned by `SettingsPageHandler.compute()` when home-app emits
`INSTANCE_CONFIG__GET_SETTINGS_PAGE`; home-app renders it at
``/plugin-io/settings/<section_key>/``.

The effect carries:

- `section_key`: the same value as the handler's `SECTION_KEY`.
- `title` / `description`: rendered at the top of the page.
- `category`: a grouping label. Defaults to "General".
- `record_count`: optional count shown next to the title.
- `form_fields`: the field list, each a :class:`FormField` describing one
  input via the widget primitives in :mod:`canvas_sdk.effects.form`.
- `audit_footer`: optional free-form footer, e.g. "Last saved 2026-05-22 by
  Plugin Author".
"""

import json
from typing import Any

from pydantic_core import InitErrorDetails

from canvas_sdk.effects import Effect, _BaseEffect
from canvas_sdk.effects.form import FormField


class SettingsPageForm(_BaseEffect):
    """Render a settings-page form."""

    class Meta:
        effect_type = "SHOW_SETTINGS_PAGE_FORM"
        apply_required_fields = ("section_key", "title", "form_fields")

    section_key: str | None = None
    title: str | None = None
    description: str | None = None
    category: str = "General"
    record_count: int | None = None
    form_fields: list[FormField] = []
    audit_footer: str | None = None

    @property
    def values(self) -> dict[str, Any]:
        """Serialize the form for the renderer."""
        return {
            "section_key": self.section_key,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "record_count": self.record_count,
            "form": [field.to_dict() for field in self.form_fields],
            "audit_footer": self.audit_footer,
        }

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        if method == "apply" and not self.form_fields:
            errors.append(
                self._create_error_detail(
                    "missing",
                    "Field 'form_fields' must contain at least one FormField.",
                    self.form_fields,
                )
            )
        return errors

    def apply(self) -> Effect:
        """Build the protobuf Effect."""
        self._validate_before_effect("apply")
        return Effect(
            type=self.Meta.effect_type,
            payload=json.dumps({"data": self.values}),
        )


__exports__ = ("SettingsPageForm",)
