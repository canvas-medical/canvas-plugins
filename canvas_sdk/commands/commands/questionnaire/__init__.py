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


class QuestionnaireCommand(_BaseCommand):
    """A class for managing a Questionnaire command within a specific note."""

    class Meta:
        key = "questionnaire"
        commit_required_fields = ("questionnaire_id",)

    QUESTION_CLASSES: dict[str, type[BaseQuestion]] = {
        ResponseOption.TYPE_TEXT: TextQuestion,
        ResponseOption.TYPE_INTEGER: IntegerQuestion,
        ResponseOption.TYPE_RADIO: RadioQuestion,
        ResponseOption.TYPE_CHECKBOX: CheckboxQuestion,
    }

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
        """Returns a list of question objects.

        For each question in the questionnaire, creates an instance of the
        appropriate question subclass based on the question.response_option_set.type.
        """
        question_objs: list[BaseQuestion] = []
        if not self._questionnaire:
            return question_objs

        for question in self._questionnaire.questions.all():
            response_options = (
                [
                    ResponseOption(dbid=o.pk, name=o.name, code=o.code, value=o.value)
                    for o in question.response_option_set.options.all()
                ]
                if question.response_option_set
                else []
            )

            qdata: dict[str, Any] = {
                "name": f"question-{question.pk}",
                "label": question.name,
                "coding": {
                    "system": question.code_system,
                    "code": question.code,
                },
                "options": response_options,
            }
            q_type = question.response_option_set.type if question.response_option_set else None
            if q_type in QuestionnaireCommand.QUESTION_CLASSES:
                question_objs.append(QuestionnaireCommand.QUESTION_CLASSES[q_type](**qdata))
            else:
                raise ValueError(f"Unsupported question type: {q_type}")

        return question_objs

    @property
    def values(self) -> dict:
        """Return the values for the command.

        For questionnaire-related commands, this includes the responses to the questions.
        """
        return {
            **super().values,
            "questions": {q.name: q.response for q in self.questions if q.response is not None},
        }
