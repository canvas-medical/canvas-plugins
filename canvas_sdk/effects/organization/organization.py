import json
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.effects import Effect


class TaxIdType(StrEnum):
    """api.Organization.TAX_ID_TYPE_CHOICES."""

    EIN = "E"
    SSN = "S"


class Organization(TrackableFieldsModel):
    """
    Effect to update the Organization (single-record).

    There is no Create / Delete: every Canvas instance has exactly one
    Organization row, provisioned at instance creation.
    """

    class Meta:
        effect_type = "ORGANIZATION"

    full_name: str | None = None
    short_name: str | None = None
    main_location_id: str | UUID | None = None
    tax_id: str | None = None
    tax_id_type: TaxIdType | None = Field(default=None, strict=False)
    group_npi_number: str | None = None
    group_taxonomy_number: str | None = None
    include_zz_qualifier: bool | None = None
    phone: str | None = None
    fax: str | None = None
    email: str | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        return super()._get_error_details(method)

    def update(self) -> Effect:
        """Update the Organization."""
        self._validate_before_effect("update")
        return Effect(
            type=f"UPDATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )


class OrganizationBranding(TrackableFieldsModel):
    """
    Effect to update the Organization's branding fields (logo, login background,
    header color, gradient). Same backing row as Organization but a distinct
    effect so plugin authors can keep the surface areas clean.
    """

    class Meta:
        effect_type = "ORGANIZATION_BRANDING"

    logo_url: str | None = None
    background_image_url: str | None = None
    header_color: str | None = None
    background_gradient: str | None = None

    def update(self) -> Effect:
        """Update branding fields."""
        self._validate_before_effect("update")
        return Effect(
            type=f"UPDATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )


class OrganizationSetting(TrackableFieldsModel):
    """
    Effect to upsert an OrganizationSetting (name/value config row).
    """

    class Meta:
        effect_type = "ORGANIZATION_SETTING"

    name: str | None = None
    value: Any | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        if method == "upsert" and not self.name:
            errors.append(
                self._create_error_detail(
                    "missing",
                    "Field 'name' is required to upsert an organization setting.",
                    self.name,
                )
            )
        return errors

    def upsert(self) -> Effect:
        """Upsert an OrganizationSetting."""
        self._validate_before_effect("upsert")
        return Effect(
            type=f"UPSERT_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )


__exports__ = ("Organization", "OrganizationBranding", "OrganizationSetting", "TaxIdType")
