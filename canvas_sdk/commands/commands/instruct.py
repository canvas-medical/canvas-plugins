from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand as BaseCommand
from canvas_sdk.commands.constants import CodeSystems, Coding
from canvas_sdk.v1.data import Command


class InstructCommand(BaseCommand):
    """A class for managing an Instruct command within a specific note."""

    class Meta:
        key = "instruct"

    coding: Coding | None = Field(default=None, json_schema_extra={"commands_api_name": "instruct"})
    comment: str | None = None

    def _get_error_details(self, method: str) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if method == "commit" and self.command_uuid:
            cmd = Command.objects.get(id=self.command_uuid)
            if not cmd.data.get("coding"):
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Field 'coding' is required in order to commit an InstructCommand.",
                        None,
                    )
                )

        if (
            self.coding
            and self.coding["system"] != CodeSystems.SNOMED
            and self.coding["system"] != CodeSystems.UNSTRUCTURED
        ):
            message = f"The 'coding.system' field must be '{CodeSystems.SNOMED}' or '{CodeSystems.UNSTRUCTURED}'."
            errors.append(self._create_error_detail("value", message, self.coding))

        return errors


__exports__ = ("InstructCommand",)
