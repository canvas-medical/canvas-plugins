from decimal import Decimal
from enum import Enum

from pydantic import Field

from canvas_sdk.commands.base import _BaseCommand


class PrescribeCommand(_BaseCommand):
    """A class for managing a Prescribe command within a specific note."""

    class Meta:
        key = "prescribe"

    class Substitutions(Enum):
        ALLOWED = "allowed"
        NOT_ALLOWED = "not_allowed"

    fdb_code: str = Field(json_schema_extra={"commands_api_name": "prescribe"})
    icd10_codes: list[str] | None = Field(
        None, json_schema_extra={"commandsd_api_name": "indications"}
    )
    sig: str
    days_supply: int | None = None
    quantity_to_dispense: Decimal
    type_to_dispense: str
    refills: int
    substitutions: Substitutions = Substitutions.ALLOWED  # type: ignore
    pharmacy: str | None = None
    prescriber_id: str = Field(json_schema_extra={"commands_api_name": "prescriber"})
    note_to_pharmacist: str | None = None

    @property
    def values(self) -> dict:
        """The Prescribe command's field values."""
        return {
            "fdb_code": self.fdb_code,
            "icd10_codes": self.icd10_codes,
            "sig": self.sig,
            "days_supply": self.days_supply,
            "quantity_to_dispense": self.quantity_to_dispense,
            "type_to_dispense": self.type_to_dispense,
            "refills": self.refills,
            "substitutions": self.substitutions,
            "pharmacy": self.pharmacy,
            "prescriber_id": self.prescriber_id,
            "note_to_pharmacist": self.note_to_pharmacist,
        }
