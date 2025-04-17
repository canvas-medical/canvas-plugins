from typing import Any
from uuid import UUID

from pydantic import Field

from canvas_sdk.effects.base import EffectType, _BaseEffect


class FormResult(_BaseEffect):
    """An Effect that will decide which forms (questionnaires) appear on the patient portal."""

    class Meta:
        effect_type = EffectType.PATIENT_PORTAL__FORM_RESULT

    questionnaire_id: str | UUID = Field(..., description="The ID of the questionnaire.")
    create_command: bool = False
    note_id: str | UUID | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The FormResults's values."""
        return {
            "questionnaire_id": str(self.questionnaire_id),
            "create_command": self.create_command,
            "note_id": str(self.note_id) if self.note_id else None,
        }

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"data": self.values}


__exports__ = ("FormResult",)
