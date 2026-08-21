from datetime import date
from typing import Any
from uuid import UUID

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand
from canvas_sdk.v1.data.vaccine import Vaccine, VaccineLot

LOT_NUMBER_MAX_LENGTH = 20


class ImmunizeCommand(_BaseCommand):
    """A class for managing an Immunize command within a specific note."""

    class Meta:
        key = "immunize"

    vaccine_id: UUID | None = None
    lot_id: UUID | None = None
    lot_number: str | None = Field(default=None, max_length=LOT_NUMBER_MAX_LENGTH)
    manufacturer: str | None = Field(default=None, max_length=100)
    expiration_date: date | None = None
    sig: str | None = Field(default=None, max_length=75)
    consent_given: bool | None = None
    given_by_id: str | None = None

    @property
    def values(self) -> dict[str, Any]:
        """Fill in the lot's manufacturer and expiration unless the caller set their own.

        Only fields the caller left untouched are derived. Anything set explicitly is
        passed through, including an explicit ``None``.
        """
        values = super().values

        if not self.lot_id or not self.is_dirty("lot_id"):
            return values

        prefill_fields = [
            field for field in ("manufacturer", "expiration_date") if not self.is_dirty(field)
        ]
        if not prefill_fields:
            return values

        lot = VaccineLot.objects.filter(id=self.lot_id).only("mvx_code", "expiration_date").first()
        if not lot:
            return values

        if "manufacturer" in prefill_fields and lot.mvx_code:
            values["manufacturer"] = lot.get_mvx_code_display()

        if "expiration_date" in prefill_fields and lot.expiration_date:
            values["expiration_date"] = lot.expiration_date.isoformat()

        return values

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if self.vaccine_id and not Vaccine.objects.filter(id=self.vaccine_id, active=True).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"No active vaccine found with id: {self.vaccine_id}.",
                    self.vaccine_id,
                )
            )

        if self.lot_id and self.lot_number:
            errors.append(
                self._create_error_detail(
                    "value",
                    "Only one of 'lot_id' and 'lot_number' may be set.",
                    self.lot_id,
                )
            )
        elif self.lot_id:
            lot = (
                VaccineLot.objects.filter(id=self.lot_id)
                .select_related("vaccine")
                .only("vaccine__id")
                .first()
            )
            if not lot:
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Vaccine lot with id {self.lot_id} not found.",
                        self.lot_id,
                    )
                )
            elif self.vaccine_id and (not lot.vaccine or lot.vaccine.id != self.vaccine_id):
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Vaccine lot {self.lot_id} does not belong to vaccine {self.vaccine_id}.",
                        self.lot_id,
                    )
                )

        return errors


__exports__ = ("ImmunizeCommand",)
