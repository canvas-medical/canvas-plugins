from enum import StrEnum

from pydantic import Field

from canvas_sdk.effects._config_crud import ConfigCrudEffect


class TaxIdType(StrEnum):
    """Tax id kind: EIN or SSN."""

    EIN = "E"
    SSN = "S"


class PracticeLocation(ConfigCrudEffect):
    """Create, update, or delete a practice location. ``id`` is the location's id.

    A new location gets the default per-location settings.
    """

    class Meta:
        effect_type = "PRACTICE_LOCATION"

    _entity_label: str = "practice location"
    _create_required: tuple[str, ...] = ("full_name", "short_name")

    full_name: str | None = None
    short_name: str | None = None
    place_of_service_code: str | None = None
    active: bool | None = None
    npi_number: str | None = None
    bill_through_organization: bool | None = None
    tax_id: str | None = None
    tax_id_type: TaxIdType | None = Field(default=None, strict=False)
    billing_location_name: str | None = None
    group_npi_number: str | None = None
    taxonomy_number: str | None = None
    include_zz_qualifier: bool | None = None
    background_image_url: str | None = None
    background_gradient: str | None = None
    header_color: str | None = None


__exports__ = ("PracticeLocation", "TaxIdType")
