from datetime import date
from enum import Enum

from canvas_sdk.commands.base import _BaseCommand as BaseCommand


class AllergyCommand(BaseCommand):
    """A class for managing an Allergy command within a specific note."""

    class Meta:
        key = "allergy"
        commit_required_fields = ("allergy",)

    class Severity(Enum):
        MILD = "mild"
        MODERATE = "moderate"
        SEVERE = "severe"

    allergy: str | None = None
    severity: Severity | None = None
    narrative: str | None = None
    approximate_date: date | None = None

    @property
    def values(self) -> dict:
        """The Allergy command's field values."""
        return {
            "allergy": self.allergy,
            "severity": self.severity.value if self.severity else None,
            "narrative": self.narrative,
            "approximate_date": (
                self.approximate_date.isoformat() if self.approximate_date else None
            ),
        }
