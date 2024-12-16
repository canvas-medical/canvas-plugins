from canvas_sdk.commands.commands.questionnaire import QuestionnaireCommand


class StructuredAssessmentCommand(QuestionnaireCommand):
    """A class for managing physical exam command."""

    class Meta:
        key = "structuredAssessment"
        commit_required_fields = ("questionnaire_id",)
