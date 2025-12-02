from typing import Any

from canvas_sdk.effects.base import EffectType, _BaseEffect
from canvas_sdk.questionnaires.utils import QuestionnaireConfig, to_yaml, validate_yaml


class CreateQuestionnaire(_BaseEffect):
    """CreateQuestionnaire effect.

    Creates a questionnaire from a QuestionnaireConfig TypedDict.
    Validates the config against JSON schema when applying the effect.

    Example:
        from canvas_sdk.questionnaires.utils import QuestionnaireConfig

        config: QuestionnaireConfig = {
            "name": "PHQ-9",
            "form_type": "QUES",
            "code_system": "LOINC",
            "code": "44249-1",
            "can_originate_in_charting": True,
            "questions": [...]
        }
        effect = CreateQuestionnaire(questionnaire_config=config)
    """

    class Meta:
        effect_type = EffectType.CREATE_QUESTIONNAIRE
        apply_required_fields = ("questionnaire_config",)

    questionnaire_config: QuestionnaireConfig

    @property
    def values(self) -> dict[str, Any]:
        """Convert config to YAML and validate."""
        yaml_string = to_yaml(self.questionnaire_config)
        validated_config = validate_yaml(yaml_string)

        return {
            "questionnaire_yaml": to_yaml(validated_config),
        }

    @property
    def effect_payload(self) -> dict[str, Any]:
        """Override to send payload without 'data' wrapper for Canvas compatibility."""
        return self.values


__exports__ = ("CreateQuestionnaire",)
