from decimal import Decimal
from enum import Enum

from pydantic import Field

from canvas_sdk.commands.base import _BaseCommand


class PrescribeCommand(_BaseCommand):
    """A class for managing a Prescribe command within a specific note."""

    class Meta:
        key = "prescribe"
        originate_required_fields = (
            "fdb_code",
            "sig",
            "quantity_to_dispense",
            "type_to_dispense",
            "refills",
            "substitutions",
            "prescriber_id",
        )

    class Substitutions(Enum):
        ALLOWED = "allowed"
        NOT_ALLOWED = "not_allowed"

    fdb_code: str | None = Field(default=None, json_schema_extra={"commands_api_name": "prescribe"})
    icd10_codes: list[str] | None = Field(
        None, json_schema_extra={"commands_api_name": "indications"}
    )
    sig: str | None = None
    days_supply: int | None = None
    quantity_to_dispense: Decimal | float | int | None = None
    type_to_dispense: str | None = None
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
        return {
            "fdb_code": self.fdb_code,
            "icd10_codes": self.icd10_codes,
            "sig": self.sig,
            "days_supply": self.days_supply,
            "quantity_to_dispense": (
                str(Decimal(self.quantity_to_dispense)) if self.quantity_to_dispense else None
            ),
            # "type_to_dispense": self.type_to_dispense,
            "refills": self.refills,
            "substitutions": self.substitutions.value if self.substitutions else None,
            "pharmacy": self.pharmacy,
            "prescriber_id": self.prescriber_id,
            "note_to_pharmacist": self.note_to_pharmacist,
        }
