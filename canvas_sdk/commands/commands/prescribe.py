from decimal import Decimal
from enum import Enum

from pydantic import Field, conlist

from canvas_sdk.commands.base import _BaseCommand
from canvas_sdk.commands.constants import ClinicalQuantity


class PrescribeCommand(_BaseCommand):
    """A class for managing a Prescribe command within a specific note."""

    class Meta:
        key = "prescribe"

    class Substitutions(Enum):
        ALLOWED = "allowed"
        NOT_ALLOWED = "not_allowed"

    fdb_code: str | None = Field(default=None, json_schema_extra={"commands_api_name": "prescribe"})
    icd10_codes: conlist(str, max_length=2) = Field(  # type: ignore[valid-type]
        default=[], json_schema_extra={"commands_api_name": "indications"}
    )
    sig: str = ""
    days_supply: int | None = None
    quantity_to_dispense: Decimal | float | int | None = None
    type_to_dispense: ClinicalQuantity | None = None
    refills: int | None = None
    substitutions: Substitutions | None = None
    pharmacy: str | None = None
    prescriber_id: str | None = Field(
        default=None, json_schema_extra={"commands_api_name": "prescriber"}
    )
    note_to_pharmacist: str | None = None

    @property
    def values(self) -> dict:
        """The Prescribe command's field values."""
        values = super().values

        if self.is_dirty("quantity_to_dispense"):
            values["quantity_to_dispense"] = (
                str(Decimal(self.quantity_to_dispense)) if self.quantity_to_dispense else None
            )

        return values


__exports__ = (
    "PrescribeCommand",
    # Not defined here but used in a current plugin
    "ClinicalQuantity",
    "Decimal",
)
