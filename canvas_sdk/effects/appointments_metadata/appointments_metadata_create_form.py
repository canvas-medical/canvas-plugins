from canvas_sdk.effects import EffectType
from canvas_sdk.effects.form import BaseCreateFormEffect, FormField, InputType  # noqa


class AppointmentsMetadataCreateFormEffect(BaseCreateFormEffect):
    """An Effect that will create a form."""

    class Meta:
        effect_type = EffectType.APPOINTMENT__FORM__CREATE_ADDITIONAL_FIELDS


__exports__ = ("AppointmentsMetadataCreateFormEffect", "FormField", "InputType")
