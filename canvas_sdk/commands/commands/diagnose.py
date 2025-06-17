from datetime import date

from pydantic import Field

from canvas_sdk.commands.base import _BaseCommand


class DiagnoseCommand(_BaseCommand):
    """A class for managing a Diagnose command within a specific note."""

    class Meta:
        key = "diagnose"

    icd10_code: str | None = Field(
        default=None, json_schema_extra={"commands_api_name": "diagnose"}
    )
    background: str | None = None
    approximate_date_of_onset: date | None = None
    today_assessment: str | None = None


__exports__ = ("DiagnoseCommand",)
