from canvas_sdk.commands.commands.questionnaire import QuestionnaireCommand


class StructuredAssessmentCommand(QuestionnaireCommand):
    """A class for managing physical exam command."""

    class Meta:
        key = "structuredAssessment"


__exports__ = ("StructuredAssessmentCommand",)
