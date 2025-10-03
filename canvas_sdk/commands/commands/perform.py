from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand as BaseCommand
from canvas_sdk.commands.constants import CodeSystems, Coding


class PerformCommand(BaseCommand):
    """A class for managing a Perform command within a specific note."""

    class Meta:
        key = "perform"

    cpt_code: str | Coding | None = Field(
        default=None, json_schema_extra={"commands_api_name": "perform"}
    )
    notes: str | None = None

    def _get_error_details(self, method: str) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if (
            isinstance(self.cpt_code, dict)
            and self.cpt_code["system"] != CodeSystems.CPT
            and self.cpt_code["system"] != CodeSystems.UNSTRUCTURED
        ):
            message = f"The 'coding.system' field must be '{CodeSystems.CPT}' or '{CodeSystems.UNSTRUCTURED}'."
            errors.append(self._create_error_detail("value", message, self.cpt_code))

        return errors


__exports__ = ("PerformCommand",)
