from pydantic import Field

from canvas_sdk.commands.base import _BaseCommand


class QuestionnaireCommand(_BaseCommand):
    """A class for managing a Questionnaire command within a specific note."""

    class Meta:
        key = "questionnaire"
        originate_required_fields = ("questionnaire_id",)

    questionnaire_id: str | None = Field(
        default=None, json_schema_extra={"commands_api_name": "questionnaire"}
    )
    result: str | None = None

    @property
    def values(self) -> dict:
        """The Questionnaire command's field values."""
        return {"questionnaire_id": self.questionnaire_id, "result": self.result}
