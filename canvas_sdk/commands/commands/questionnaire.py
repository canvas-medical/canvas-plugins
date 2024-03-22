from canvas_sdk.commands.commands.base import _BaseCommand


class QuestionnaireCommand(_BaseCommand):
    """A class for managing a Questionnaire command within a specific note."""

    class Meta:
        key = "questionnaire"

    questionnaire_id: int
    result: str | None = None

    @property
    def values(self) -> dict:
        """The Questionnaire command's field values."""
        return {"questionnaire_id": self.questionnaire_id, "result": self.result}
