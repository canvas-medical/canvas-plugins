from canvas_sdk.commands.commands.questionnaire import QuestionnaireCommand


class ReviewOfSystemsCommand(QuestionnaireCommand):
    """A class for managing physical exam command."""

    class Meta:
        key = "ros"
        commit_required_fields = ("questionnaire_id",)


__canvas_allowed_attributes__ = ("ReviewOfSystemsCommand",)
