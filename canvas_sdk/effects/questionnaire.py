from typing import Any

from canvas_sdk.effects.base import EffectType, _BaseEffect


class CreateQuestionnaire(_BaseEffect):
    """CreateQuestionnaire effect.

    Creates a questionnaire from a YAML definition by passing it to the
    YamlQuestionnaireComposer on the Canvas side.
    """

    class Meta:
        effect_type = EffectType.CREATE_QUESTIONNAIRE
        apply_required_fields = ("questionnaire_yaml",)

    questionnaire_yaml: str

    @property
    def values(self) -> dict[str, Any]:
        """Make the payload."""
        return {
            "questionnaire_yaml": self.questionnaire_yaml,
        }

    @property
    def effect_payload(self) -> dict[str, Any]:
        """Override to send payload without 'data' wrapper for Canvas compatibility."""
        return self.values


__exports__ = ("CreateQuestionnaire",)
