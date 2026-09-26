from enum import StrEnum
from uuid import UUID

from pydantic import Field

from canvas_sdk.effects._config_crud import ConfigCrudEffect


class PracticeLocationAddressUse(StrEnum):
    """What a practice location address is used for."""

    HOME = "home"
    WORK = "work"
    TEMP = "temp"
    OLD = "old"
    BILLING = "billing"


class PracticeLocationAddressType(StrEnum):
    """Postal, physical, or both."""

    POSTAL = "postal"
    PHYSICAL = "physical"
    BOTH = "both"


class PracticeLocationAddress(ConfigCrudEffect):
    """Create, update, or delete a practice location's address.

    ``id`` is the address's id and ``practice_location_id`` the location's id.
    """

    class Meta:
        effect_type = "PRACTICE_LOCATION_ADDRESS"

    _entity_label: str = "practice location address"
    _create_required: tuple[str, ...] = (
        "practice_location_id",
        "line1",
        "city",
        "state_code",
        "postal_code",
        "country",
    )

    practice_location_id: str | UUID | None = None
    line1: str | None = None
    line2: str | None = None
    city: str | None = None
    district: str | None = None
    state_code: str | None = None
    postal_code: str | None = None
    country: str | None = None
    use: PracticeLocationAddressUse | None = Field(default=None, strict=False)
    type: PracticeLocationAddressType | None = Field(default=None, strict=False)


__exports__ = (
    "PracticeLocationAddress",
    "PracticeLocationAddressType",
    "PracticeLocationAddressUse",
)
