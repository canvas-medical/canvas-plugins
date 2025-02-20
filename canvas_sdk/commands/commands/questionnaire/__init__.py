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

    questionnaire_id: str | None = Field(
        default=None, json_schema_extra={"commands_api_name": "questionnaire"}
    )
    result: str | None = None

    @cached_property
    def _questionnaire(self) -> Questionnaire:
        if not self.questionnaire_id:
            raise ValueError("questionnaire_id is required for QuestionnaireCommand")
        return Questionnaire.objects.get(id=self.questionnaire_id)

    @cached_property
    def questions(self) -> list[BaseQuestion]:
        """
        Returns a list of question objects.

        For each question in the questionnaire, creates an instance of the
        appropriate question subclass based on the question.response_option_set.type.
        """
        question_objs: list[BaseQuestion] = []
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
            q_obj: BaseQuestion
            if q_type == ResponseOption.TYPE_TEXT:
                q_obj = TextQuestion(**qdata)
            elif q_type == ResponseOption.TYPE_INTEGER:
                q_obj = IntegerQuestion(**qdata)
            elif q_type == ResponseOption.TYPE_RADIO:
                q_obj = RadioQuestion(**qdata)
            elif q_type == ResponseOption.TYPE_CHECKBOX:
                q_obj = CheckboxQuestion(**qdata)
            else:
                # This should never happen, but just in case
                raise ValueError(f"Unsupported question type: {q_type}")
            question_objs.append(q_obj)
        return question_objs

    @property
    def values(self) -> dict:
        """Return the values for the command.

        For questionnaire-related commands, this includes the responses to the questions.
        """
        values = super().values

        values["questions"] = {q.name: q.response for q in self.questions if q.response is not None}

        return values
