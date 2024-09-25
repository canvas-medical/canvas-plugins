from datetime import date

from pydantic import Field

from canvas_sdk.commands.base import _BaseCommand as BaseCommand


class PastSurgicalHistoryCommand(BaseCommand):
    """A class for managing a Past Surgical History command within a specific note."""

    class Meta:
        key = "surgicalHistory"
        commit_required_fields = ("past_surgical_history",)

    past_surgical_history: str | None = None
    approximate_date: date | None = None
    comment: str | None = Field(max_length=1000, default=None)

    @property
    def values(self) -> dict:
        """The Past Surgical History command's field values."""
        return {
            "past_surgical_history": self.past_surgical_history,
            "approximate_date": (
                self.approximate_date.isoformat() if self.approximate_date else None
            ),
            "comment": self.comment,
        }
