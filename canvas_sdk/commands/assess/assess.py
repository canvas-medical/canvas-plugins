from canvas_sdk.commands.assess.constants import AssessStatus
from canvas_sdk.commands.base import _BaseCommand


class AssessCommand(_BaseCommand):
    """A class for managing an Assess command within a specific note."""

    condition_id: int | None = None
    background: str | None = None
    status: AssessStatus | None = None
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
