from canvas_sdk.commands.commands.questionnaire import QuestionnaireCommand
from canvas_sdk.commands.commands.questionnaire.toggle_questions import ToggleQuestionsMixin


class StructuredAssessmentCommand(ToggleQuestionsMixin, QuestionnaireCommand):
    """A class for managing physical exam command."""

    class Meta:
        key = "structuredAssessment"


__exports__ = ("StructuredAssessmentCommand",)
