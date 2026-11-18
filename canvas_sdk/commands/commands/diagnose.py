from pydantic import Field

from canvas_sdk.commands.base import _BaseCommand
from canvas_sdk.commands.constants import ApproximateDate


class DiagnoseCommand(_BaseCommand):
    """A class for managing a Diagnose command within a specific note."""

    class Meta:
        key = "diagnose"

    icd10_code: str | None = Field(
        default=None, json_schema_extra={"commands_api_name": "diagnose"}
    )
    background: str | None = None
    approximate_date_of_onset: ApproximateDate | None = None
    today_assessment: str | None = Field(default=None, max_length=2048)


__exports__ = ("DiagnoseCommand",)
