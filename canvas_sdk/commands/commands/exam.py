from canvas_sdk.commands.commands.questionnaire import QuestionnaireCommand


class PhysicalExamCommand(QuestionnaireCommand):
    """A class for managing physical exam command."""

    class Meta:
        key = "exam"


__exports__ = ("PhysicalExamCommand",)
