from canvas_sdk.commands.commands.questionnaire import QuestionnaireCommand


class ReviewOfSystemsCommand(QuestionnaireCommand):
    """A class for managing physical exam command."""

    class Meta:
        key = "ros"


__exports__ = ("ReviewOfSystemsCommand",)
