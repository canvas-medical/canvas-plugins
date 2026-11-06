from canvas_sdk.commands.commands.assessment_link import _AssessmentLinkedCommand
from canvas_sdk.commands.commands.questionnaire import QuestionnaireCommand


class StructuredAssessmentCommand(_AssessmentLinkedCommand, QuestionnaireCommand):
    """A class for managing a Structured Assessment command within a specific note."""

    class Meta:
        key = "structuredAssessment"


__exports__ = ("StructuredAssessmentCommand",)
