from datetime import date

from pydantic import Field

from canvas_sdk.commands.base import _BaseCommand as BaseCommand


class PastSurgicalHistoryCommand(BaseCommand):
    """A class for managing a Past Surgical History command within a specific note."""

    class Meta:
        key = "surgicalHistory"

    past_surgical_history: str | None = None
    approximate_date: date | None = None
    comment: str | None = Field(max_length=1000, default=None)


__exports__ = ("PastSurgicalHistoryCommand",)
