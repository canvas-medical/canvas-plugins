from datetime import date

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand as BaseCommand
from canvas_sdk.commands.constants import CodeSystems, Coding


class PastSurgicalHistoryCommand(BaseCommand):
    """A class for managing a Past Surgical History command within a specific note."""

    class Meta:
        key = "surgicalHistory"

    past_surgical_history: str | Coding | None = None
    approximate_date: date | None = None
    comment: str | None = Field(max_length=1000, default=None)

    def _get_error_details(self, method: str) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if (
            isinstance(self.past_surgical_history, dict)
            and self.past_surgical_history["system"] != CodeSystems.SNOMED
            and self.past_surgical_history["system"] != CodeSystems.UNSTRUCTURED
        ):
            message = f"The 'coding.system' field must be '{CodeSystems.SNOMED}' or '{CodeSystems.UNSTRUCTURED}'."
            errors.append(self._create_error_detail("value", message, self.past_surgical_history))

        return errors


__exports__ = ("PastSurgicalHistoryCommand",)
