from canvas_sdk.effects import EffectType
from canvas_sdk.effects.form import BaseCreateFormEffect, FormField, InputType  # noqa


class PatientMetadataCreateFormEffect(BaseCreateFormEffect):
    """An Effect that will create a form."""

    class Meta:
        effect_type = EffectType.PATIENT_METADATA__CREATE_ADDITIONAL_FIELDS


__exports__ = ("PatientMetadataCreateFormEffect", "FormField", "InputType")
