from datetime import datetime

from pydantic import Field

from canvas_sdk.commands.base import _BaseCommand
from canvas_sdk.commands.constants import Coding


class DiagnoseCommand(_BaseCommand):
    """A class for managing a Diagnose command within a specific note."""

    class Meta:
        key = "diagnose"
        commit_required_fields = ("icd10_code",)

    icd10_code: str | None = Field(
        default=None, json_schema_extra={"commands_api_name": "diagnose"}
    )
    background: str | None = None
    approximate_date_of_onset: datetime | None = None
    today_assessment: str | None = None

    @property
    def values(self) -> dict:
        """The Diagnose command's field values."""
        return {
            "icd10_code": self.icd10_code,
            "background": self.background,
            "approximate_date_of_onset": (
                self.approximate_date_of_onset.isoformat()
                if self.approximate_date_of_onset
                else None
            ),
            "today_assessment": self.today_assessment,
        }

    @property
    def coding_filter(self) -> Coding:
        """The coding filter used for command insertion in protocol cards."""
        return {"code": self.icd10_code, "system": "icd10cm"}
