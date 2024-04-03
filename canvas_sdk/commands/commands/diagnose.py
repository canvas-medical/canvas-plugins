from datetime import datetime

from pydantic import Field

from canvas_sdk.commands.base import _BaseCommand


class DiagnoseCommand(_BaseCommand):
    """A class for managing a Diagnose command within a specific note."""

    class Meta:
        key = "diagnose"

    icd10_code: str = Field(json_schema_extra={"commands_api_name": "diagnose"})
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


# how do we make sure icd10_code is a valid code?

# idea1:
# create an auto-generated enum class of all possible icd10s, then type the field as that enum
# will require releasing a new version with the new codes every year, and devs will need to update
# to make sure they have the latest version to get the right set of codes.

# idea2:
# see if we can get ValueSets to play nicely with pydantic

# idea3: runtime warning after pinging ontologies
