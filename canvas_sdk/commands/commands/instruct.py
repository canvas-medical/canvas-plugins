from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand as BaseCommand
from canvas_sdk.commands.constants import CodeSystems, Coding


class InstructCommand(BaseCommand):
    """A class for managing an Instruct command within a specific note."""

    class Meta:
        key = "instruct"
        commit_required_fields = ("instruction",)

    coding: Coding | None = None
    comment: str | None = None

    def _get_error_details(self, method: str) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if (
            self.coding
            and self.coding["system"] != CodeSystems.SNOMED
            and self.coding["system"] != CodeSystems.UNSTRUCTURED
        ):
            message = f"The 'coding.system' field must be '{CodeSystems.SNOMED}' or '{CodeSystems.UNSTRUCTURED}'."
            errors.append(self._create_error_detail("value", message, self.coding))

        return errors
