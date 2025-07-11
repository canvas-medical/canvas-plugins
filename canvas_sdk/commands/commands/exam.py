from canvas_sdk.commands.commands.questionnaire import QuestionnaireCommand
from canvas_sdk.commands.commands.questionnaire.toggle_questions import ToggleQuestionsMixin


class PhysicalExamCommand(ToggleQuestionsMixin, QuestionnaireCommand):
    """A class for managing physical exam command."""

    class Meta:
        key = "exam"


__exports__ = ("PhysicalExamCommand",)
