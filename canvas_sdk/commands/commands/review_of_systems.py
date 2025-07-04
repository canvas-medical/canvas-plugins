from canvas_sdk.commands.commands.questionnaire import QuestionnaireCommand
from canvas_sdk.commands.commands.questionnaire.toggle_questions import ToggleQuestionsMixin


class ReviewOfSystemsCommand(ToggleQuestionsMixin, QuestionnaireCommand):
    """A class for managing physical exam command."""

    class Meta:
        key = "ros"


__exports__ = ("ReviewOfSystemsCommand",)
