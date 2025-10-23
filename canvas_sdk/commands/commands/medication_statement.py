from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand
from canvas_sdk.commands.constants import CodeSystems, Coding


class MedicationStatementCommand(_BaseCommand):
    """A class for managing a MedicationStatement command within a specific note."""

    class Meta:
        key = "medicationStatement"

    fdb_code: str | Coding | None = Field(
        default=None, json_schema_extra={"commands_api_name": "medication"}
    )
    sig: str | None = None

    def _get_error_details(self, method: str) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if (
            isinstance(self.fdb_code, dict)
            and self.fdb_code["system"] != CodeSystems.FDB
            and self.fdb_code["system"] != CodeSystems.UNSTRUCTURED
        ):
            message = f"The 'coding.system' field must be '{CodeSystems.FDB}' or '{CodeSystems.UNSTRUCTURED}'."
            errors.append(self._create_error_detail("value", message, self.fdb_code))

        return errors


# how do we make sure fdb_code is a valid code?

# idea1:
# create an auto-generated enum class of all possible fdbs, then type the field as that enum
# will require releasing a new version with the new codes every year, and devs will need to update
# to make sure they have the latest version to get the right set of codes.

# idea2:
# see if we can get ValueSets to play nicely with pydantic

__exports__ = ("MedicationStatementCommand",)
