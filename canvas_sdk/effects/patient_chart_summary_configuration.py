from enum import Enum
from typing import Any

from pydantic import Field

from canvas_sdk.effects.base import EffectType, _BaseEffect


class PatientChartSummaryConfiguration(_BaseEffect):
    """
    An Effect that will decide which sections appear on the patient's chart summary in Canvas.
    """

    class Meta:
        effect_type = EffectType.SHOW_PATIENT_CHART_SUMMARY_SECTIONS

    class Section(Enum):
        SOCIAL_DETERMINANTS = "social_determinants"
        GOALS = "goals"
        CONDITIONS = "conditions"
        MEDICATIONS = "medications"
        ALLERGIES = "allergies"
        CARE_TEAMS = "care_teams"
        VITALS = "vitals"
        IMMUNIZATIONS = "immunizations"
        SURGICAL_HISTORY = "surgical_history"
        FAMILY_HISTORY = "family_history"
        CODING_GAPS = "coding_gaps"

    sections: list[Section] = Field(min_length=1)

    @property
    def values(self) -> dict[str, Any]:
        """The PatientChartSummaryConfiguration's values."""
        return {"sections": [s.value for s in self.sections]}

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"data": self.values}


__exports__ = ("PatientChartSummaryConfiguration",)
