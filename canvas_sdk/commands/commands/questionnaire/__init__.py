from functools import cached_property
from typing import Any

from pydantic import BaseModel, Field

from canvas_sdk.commands.base import _BaseCommand
from canvas_sdk.commands.commands.questionnaire.question import (
    BaseQuestion,
    CheckboxQuestion,
    IntegerQuestion,
    RadioQuestion,
    ResponseOption,
    TextQuestion,
)
from canvas_sdk.v1.data import Command, Questionnaire

QUESTION_CLASSES: dict[str, type[BaseQuestion]] = {
    ResponseOption.TYPE_TEXT: TextQuestion,
    ResponseOption.TYPE_INTEGER: IntegerQuestion,
    ResponseOption.TYPE_RADIO: RadioQuestion,
    ResponseOption.TYPE_CHECKBOX: CheckboxQuestion,
}


class Answer(BaseModel):
    """One question's response."""

    #: The question's id, as :attr:`QuestionnaireCommand.questions` reports it.
    question_id: int
    #: The answer, in the form the question takes: text, a number, an option's id, or a list of
    #: option ids for a checkbox.
    response: str | int | list[int]
    #: Carried onto a checkbox selection; ignored by every other question type.
    comment: str = ""


class QuestionnaireCommand(_BaseCommand):
    """A class for managing a Questionnaire command within a specific note."""

    class Meta:
        key = "questionnaire"
        commit_required_fields = ("questionnaire_id",)

    questionnaire_id: str | None = Field(
        default=None, json_schema_extra={"commands_api_name": "questionnaire"}
    )
    result: str | None = None
    #: The answers this command records, one per question. Read into :attr:`values` as responses
    #: on the matching :attr:`questions`.
    answers: list[Answer] = Field(default_factory=list)

    @cached_property
    def _questionnaire(self) -> Questionnaire | None:
        if not self.questionnaire_id:
            if command_uuid := self.command_uuid:
                # If the questionnaire is not set, try to fetch it from the command
                try:
                    command_data = Command.objects.values_list("data", flat=True).get(
                        id=command_uuid
                    )
                    if questionnaire_dbid := command_data.get("questionnaire", {}).get("value"):
                        questionnaire = Questionnaire.objects.get(dbid=questionnaire_dbid)
                        self.questionnaire_id = str(questionnaire.id)
                        return questionnaire
                except (Command.DoesNotExist, Questionnaire.DoesNotExist):
                    return None
            else:
                return None

        return Questionnaire.objects.get(id=self.questionnaire_id)  # type: ignore[misc]

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
                "id": question.pk,
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

    def _option(self, question: BaseQuestion, option_id: str) -> ResponseOption:
        """The option this question offers under this id.

        Ids are compared as text so a lone one that arrived as a string still matches.
        """
        for option in question.options:
            if str(option.dbid) == option_id:
                return option

        allowed = ", ".join(f"{option.dbid} ({option.name})" for option in question.options)
        raise ValueError(
            f"{option_id!r} is not an option for question '{question.label}'. "
            f"Allowed options: {allowed or 'none'}"
        )

    def _apply_answers(self) -> None:
        """Set each answer as a response on its question, dispatching on the question's type.

        Clears the questions :attr:`answers` names before setting them, so reading twice gives
        the same result and a response set directly on any other question is left alone.
        """
        questions = {str(question.id): question for question in self.questions}

        for answer in self.answers:
            question = questions.get(str(answer.question_id))
            if question is None:
                raise ValueError(
                    f"{answer.question_id} is not a question in questionnaire "
                    f"{self.questionnaire_id}"
                )

            question.response = None

            if question.type == ResponseOption.TYPE_TEXT:
                question.add_response(text=str(answer.response))
            elif question.type == ResponseOption.TYPE_INTEGER:
                question.add_response(integer=answer.response)
            elif question.type == ResponseOption.TYPE_RADIO:
                question.add_response(option=self._option(question, str(answer.response)))
            else:
                option_ids = (
                    [str(option_id) for option_id in answer.response]
                    if isinstance(answer.response, list)
                    else [str(answer.response)]
                )
                for option_id in option_ids:
                    question.add_response(
                        option=self._option(question, option_id), comment=answer.comment
                    )

    @property
    def values(self) -> dict:
        """Return the values for the command.

        For questionnaire-related commands, this includes the responses to the questions.
        """
        if self.answers:
            self._apply_answers()

        values = super().values
        # answers do not carry over the effect.
        values.pop("answers", None)

        values["questions"] = {q.name: q.response for q in self.questions if q.response is not None}

        return values


__exports__ = ("QUESTION_CLASSES", "Answer", "QuestionnaireCommand")
