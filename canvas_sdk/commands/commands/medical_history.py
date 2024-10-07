from datetime import date

from pydantic import Field

from canvas_sdk.commands.base import _BaseCommand as BaseCommand


class MedicalHistoryCommand(BaseCommand):
    """A class for managing a Medical History command within a specific note."""

    class Meta:
        key = "medicalHistory"
        commit_required_fields = ("past_medical_history",)

    past_medical_history: str | None = None
    approximate_start_date: date | None = None
    approximate_end_date: date | None = None
    show_on_condition_list: bool = True
    comments: str | None = Field(max_length=1000, default=None)

    @property
    def values(self) -> dict:
        """The Medical History command's field values."""
        return {
            "past_medical_history": self.past_medical_history,
            "approximate_start_date": (
                self.approximate_start_date.isoformat() if self.approximate_start_date else None
            ),
            "approximate_end_date": (
                self.approximate_end_date.isoformat() if self.approximate_end_date else None
            ),
            "show_on_condition_list": self.show_on_condition_list,
            "comments": self.comments,
        }
