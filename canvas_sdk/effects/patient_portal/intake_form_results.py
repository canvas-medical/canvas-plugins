from typing import Any

from pydantic import Field

from canvas_sdk.effects.base import EffectType, _BaseEffect


class IntakeFormResults(_BaseEffect):
    """An Effect that will decide which intake forms (questionnaires) appear on the patient portal."""

    class Meta:
        effect_type = EffectType.PATIENT_PORTAL__INTAKE_FORM_RESULTS

    questionnaire_ids: list = Field(min_length=0)

    @property
    def values(self) -> dict[str, Any]:
        """The IntakeFormResults's values."""
        return {"questionnaire_ids": [str(q) for q in self.questionnaire_ids]}

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"data": self.values}
