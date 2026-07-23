import json
from datetime import date
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.effects import Effect


class LicenseType(StrEnum):
    """Mirrors api.StaffLicense.LICENSE_TYPE_CHOICES."""

    STATE_LICENSE = "State License"
    DEA = "DEA"
    CLIA = "CLIA"
    PTAN = "PTAN"
    TAXONOMY = "Taxonomy"
    SPI = "SPI"
    OTHER = "Other"


class StaffLicense(TrackableFieldsModel):
    """
    Effect to create, update, or delete a license / credential on a Staff record.

    Example:
        StaffLicense(
            staff_id="<uuid>",
            license_type=LicenseType.DEA,
            issuing_authority_long_name="DEA",
            license_or_certification_identifier="AB1234567",
            issuance_date=date(2024, 1, 1),
            expiration_date=date(2026, 1, 1),
            state="MA",
            primary=True,
        ).create()
    """

    class Meta:
        effect_type = "STAFF_LICENSE"

    id: str | UUID | None = None
    staff_id: str | UUID | None = None
    license_type: LicenseType | None = Field(default=None, strict=False)
    issuing_authority_long_name: str | None = None
    license_or_certification_identifier: str | None = None
    state: str | None = None
    issuance_date: date | None = None
    expiration_date: date | None = None
    primary: bool | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if method == "create":
            for required in ("staff_id", "license_type", "license_or_certification_identifier"):
                if not getattr(self, required):
                    errors.append(
                        self._create_error_detail(
                            "missing",
                            f"Field '{required}' is required to create a staff license.",
                            getattr(self, required),
                        )
                    )

        if method in ("update", "delete") and not self.id:
            errors.append(
                self._create_error_detail(
                    "missing",
                    f"Field 'id' is required to {method} a staff license.",
                    self.id,
                )
            )

        return errors

    def create(self) -> Effect:
        """Create a new license/credential."""
        self._validate_before_effect("create")
        return Effect(
            type=f"CREATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )

    def update(self) -> Effect:
        """Update a license/credential."""
        self._validate_before_effect("update")
        return Effect(
            type=f"UPDATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )

    def delete(self) -> Effect:
        """Delete a license/credential."""
        self._validate_before_effect("delete")
        return Effect(
            type=f"DELETE_{self.Meta.effect_type}",
            payload=json.dumps({"data": {"id": str(self.id)}}),
        )


__exports__ = ("StaffLicense", "LicenseType")
