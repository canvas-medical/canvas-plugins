from datetime import date

from pydantic import Field

from canvas_sdk.commands.base import _BaseCommand


class AddConditionCommand(_BaseCommand):
    """A class for managing an AddCondition command within a specific note."""

    class Meta:
        key = "addCondition"

    icd10_code: str | None = Field(
        default=None, json_schema_extra={"commands_api_name": "condition"}
    )
    background: str | None = None
    approximate_date_of_onset: date | None = None
    comments: str | None = Field(default=None, max_length=1000)


__exports__ = ("AddConditionCommand",)
