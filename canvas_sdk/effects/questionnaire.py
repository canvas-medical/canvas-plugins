from typing import Any

from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect
from canvas_sdk.questionnaires.utils import QuestionnaireConfig, config_errors


class CreateQuestionnaire(_BaseEffect):
    """Create a questionnaire from a configuration built in Python.

    A questionnaire name is globally unique. Emitting this effect with a name that is already in use
    archives the existing questionnaire, renames it "<name> (v<id>)", and creates a new one in its
    place, so repeated emissions produce a chain of superseded versions rather than editing one
    questionnaire. Emit it from an explicit trigger, such as a SimpleAPI route, rather than from a
    handler that fires on a recurring event.

    apply() validates the configuration, so a malformed questionnaire raises a ValidationError
    listing every problem with it where it was written. Failures on the Canvas side are reported to
    Sentry but are not visible to the plugin.

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

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """Report every problem with the configuration, rather than stopping at the first."""
        errors = super()._get_error_details(method)

        errors.extend(
            self._create_error_detail("questionnaire", message, self.questionnaire)
            for message in config_errors(self.questionnaire)
        )

        return errors

    @property
    def values(self) -> dict[str, Any]:
        """The configuration, carrying the defaults the schema defines."""
        # apply() validates before it reads this, and that pass fills in the two
        # display_*_in_social_history_section defaults the composer requires.
        return {"questionnaire": self.questionnaire}


__exports__ = ("CreateQuestionnaire",)
