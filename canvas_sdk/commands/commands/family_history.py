from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand as BaseCommand
from canvas_sdk.commands.constants import CodeSystems, Coding


class FamilyHistoryCommand(BaseCommand):
    """A class for managing a Family History command within a specific note."""

    class Meta:
        key = "familyHistory"

    family_history: str | Coding | None = None
    relative: str | None = None
    note: str | None = None

    def _get_error_details(self, method: str) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if (
            isinstance(self.family_history, dict)
            and self.family_history["system"] != CodeSystems.SNOMED
            and self.family_history["system"] != CodeSystems.UNSTRUCTURED
        ):
            message = f"The 'coding.system' field must be '{CodeSystems.SNOMED}' or '{CodeSystems.UNSTRUCTURED}'."
            errors.append(self._create_error_detail("value", message, self.family_history))

        return errors


__exports__ = ("FamilyHistoryCommand",)
