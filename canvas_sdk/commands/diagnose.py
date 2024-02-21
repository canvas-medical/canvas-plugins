from datetime import datetime

from canvas_sdk.commands.base import _BaseCommand


class DiagnoseCommand(_BaseCommand):
    """A class for managing a Diagnose command within a specific note."""

    # how do we make sure icd10_code is a valid code?
    icd10_code: str
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
