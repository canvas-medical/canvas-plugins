from typing import Any

from canvas_sdk.effects.base import EffectType, _BaseEffect


class CreateQuestionnaireResult(_BaseEffect):
    """CreateQuestionnaireResult effect."""

    class Meta:
        effect_type = EffectType.CREATE_QUESTIONNAIRE_RESULT

    interview_id: str | None = None
    score: float | None = None
    abnormal: bool | None = None
    narrative: str | None = None
    code_system: str | None = None
    code: str | None = None

    @property
    def values(self) -> dict[str, Any]:
        """Make the payload."""
        return {
            "interview_id": self.interview_id,
            "score": self.score,
            "abnormal": self.abnormal or False,
            "narrative": self.narrative or "",
            "code_system": self.code_system,
            "code": self.code,
        }


__exports__ = ("CreateQuestionnaireResult",)
