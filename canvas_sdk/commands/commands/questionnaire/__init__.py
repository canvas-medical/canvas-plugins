from functools import cached_property
from typing import Any

from pydantic import Field

from canvas_sdk.commands.base import _BaseCommand
from canvas_sdk.commands.commands.questionnaire.question import (
    BaseQuestion,
    CheckboxQuestion,
    IntegerQuestion,
    RadioQuestion,
    ResponseOption,
    TextQuestion,
)
from canvas_sdk.v1.data import Questionnaire

QUESTION_CLASSES: dict[str, type[BaseQuestion]] = {
    ResponseOption.TYPE_TEXT: TextQuestion,
    ResponseOption.TYPE_INTEGER: IntegerQuestion,
    ResponseOption.TYPE_RADIO: RadioQuestion,
    ResponseOption.TYPE_CHECKBOX: CheckboxQuestion,
}


class QuestionnaireCommand(_BaseCommand):
    """A class for managing a Questionnaire command within a specific note."""

    class Meta:
        key = "questionnaire"
        commit_required_fields = ("questionnaire_id",)

    questionnaire_id: str | None = Field(
        default=None, json_schema_extra={"commands_api_name": "questionnaire"}
    )
    result: str | None = None

    @cached_property
    def _questionnaire(self) -> Questionnaire | None:
        if not self.questionnaire_id:
            return None
        return Questionnaire.objects.get(id=self.questionnaire_id)

    @cached_property
    def questions(self) -> list[BaseQuestion]:
        """
        Returns a list of question objects.

        For each question in the questionnaire, creates an instance of the
        appropriate question subclass based on the question.response_option_set.type.
        """
        question_objs: list[BaseQuestion] = []
        if not self._questionnaire:
            return question_objs

        for question in self._questionnaire.questions.all():
            qdata: dict[str, Any] = {
                "name": f"question-{question.pk}",
                "label": question.name,
                "coding": {
                    "system": question.code_system,
                    "code": question.code,
                },
                "options": [
                    ResponseOption(
                        dbid=option.pk, name=option.name, code=option.code, value=option.value
                    )
                    for option in question.response_option_set.options.all()
                ]
                if question.response_option_set
                else [],
            }
            q_type = question.response_option_set.type if question.response_option_set else None
            if q_type in QUESTION_CLASSES:
                question_objs.append(QUESTION_CLASSES[q_type](**qdata))
            else:
                raise ValueError(f"Unsupported question type: {q_type}")
        return question_objs

    @property
    def values(self) -> dict:
        """Return the values for the command.

        For questionnaire-related commands, this includes the responses to the questions.
        """
        values = super().values

        values["questions"] = {q.name: q.response for q in self.questions if q.response is not None}

        return values


__exports__ = ("QUESTION_CLASSES", "QuestionnaireCommand")
