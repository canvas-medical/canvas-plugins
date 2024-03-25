from canvas_sdk.commands.base import _BaseCommand
from pydantic import Field


class MedicationStatementCommand(_BaseCommand):
    """A class for managing a MedicationStatement command within a specific note."""

    class Meta:
        key = "medicationStatement"

    fdb_code: str = Field(json_schema_extra={"commands_api_name": "medication"})
    sig: str | None = None

    @property
    def values(self) -> dict:
        """The MedicationStatement command's field values."""
        return {"fdb_code": self.fdb_code, "sig": self.sig}


# how do we make sure fdb_code is a valid code?

# idea1:
# create an auto-generated enum class of all possible fdbs, then type the field as that enum
# will require releasing a new version with the new codes every year, and devs will need to update
# to make sure they have the latest version to get the right set of codes.

# idea2:
# see if we can get ValueSets to play nicely with pydantic
