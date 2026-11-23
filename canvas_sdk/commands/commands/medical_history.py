from pydantic import Field

from canvas_sdk.commands.base import _BaseCommand as BaseCommand
from canvas_sdk.commands.constants import ApproximateDate


class MedicalHistoryCommand(BaseCommand):
    """A class for managing a Medical History command within a specific note."""

    class Meta:
        key = "medicalHistory"

    past_medical_history: str | None = None
    approximate_start_date: ApproximateDate | None = None
    approximate_end_date: ApproximateDate | None = None
    show_on_condition_list: bool = True
    comments: str | None = Field(max_length=1000, default=None)


__exports__ = ("MedicalHistoryCommand",)
