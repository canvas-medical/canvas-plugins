from typing import Any, cast

from django import forms
from django.contrib.postgres.fields import ArrayField
from django.forms import SelectMultiple


class ArraySelectMultiple(SelectMultiple):
    """ArraySelectMultiple."""

    def value_omitted_from_data(self, data: Any, files: Any, name: str) -> bool:
        """Override to check if the value is omitted from data."""
        return False


class ChoiceArrayField(ArrayField):
    """ChoiceArrayField."""

    def formfield(
        self,
        form_class: type[forms.Field] | None = None,
        choices_form_class: type[forms.ChoiceField] | None = None,
        **kwargs: Any,
    ) -> forms.Field:
        """Override formfield to use a custom widget."""
        defaults = {
            "form_class": forms.TypedMultipleChoiceField,
            "choices": self.base_field.choices,
            "coerce": self.base_field.to_python,
            "widget": ArraySelectMultiple,
        }
        defaults.update(kwargs)

        return cast(forms.Field, super(ArrayField, self).formfield(**defaults))  # type: ignore[arg-type]


__exports__ = ()
