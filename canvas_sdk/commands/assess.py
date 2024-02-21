from enum import Enum

from canvas_sdk.commands.base import _BaseCommand


class AssessCommand(_BaseCommand):
    """A class for managing an Assess command within a specific note."""

    class Status(Enum):
        IMPROVED = "improved"
        STABLE = "stable"
        DETERIORATED = "deteriorated"

    # how do we make sure that condition_id is a valid condition for the patient?
    condition_id: int
    background: str | None = None
    status: Status | None = None
    narrative: str | None = None

    @property
    def values(self) -> dict:
        """The Assess command's field values."""
        return {
            "condition_id": self.condition_id,
            "background": self.background,
            "status": self.status.value if self.status else None,
            "narrative": self.narrative,
        }
