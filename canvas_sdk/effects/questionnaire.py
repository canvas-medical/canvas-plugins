from typing import Any

from canvas_sdk.effects.base import EffectType, _BaseEffect
from canvas_sdk.questionnaires.utils import QuestionnaireConfig, validate_config


class CreateQuestionnaire(_BaseEffect):
    """Create a questionnaire from a configuration built in Python.

    A questionnaire name is globally unique. Emitting this effect with a name that is already in use
    archives the existing questionnaire, renames it "<name> (v<id>)", and creates a new one in its
    place, so repeated emissions produce a chain of superseded versions rather than editing one
    questionnaire. Emit it from an explicit trigger, such as a SimpleAPI route, rather than from a
    handler that fires on a recurring event.

    The configuration is validated here, so a malformed questionnaire raises where it was written.
    Failures on the Canvas side are reported to Sentry but are not visible to the plugin.

    Example:
        config: QuestionnaireConfig = {
            "name": "PHQ-9",
            "form_type": "QUES",
            "code_system": "LOINC",
            "code": "44249-1",
            "can_originate_in_charting": True,
            "questions": [...],
        }
        CreateQuestionnaire(questionnaire=config).apply()
    """

    class Meta:
        effect_type = EffectType.CREATE_QUESTIONNAIRE
        apply_required_fields = ("questionnaire",)

    questionnaire: QuestionnaireConfig

    @property
    def values(self) -> dict[str, Any]:
        """Validate the configuration and fill in schema defaults."""
        return {"questionnaire": validate_config(self.questionnaire)}


__exports__ = ("CreateQuestionnaire",)
