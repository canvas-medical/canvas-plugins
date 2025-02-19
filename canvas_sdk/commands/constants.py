from typing import NotRequired

from pydantic import Field
from typing_extensions import TypedDict

from canvas_sdk.base import Model


class Coding(TypedDict):
    """Coding object in Canvas."""

    system: str
    code: str
    display: NotRequired[str]


class ClinicalQuantity(TypedDict):
    """A ClinicalQuantity for prescribe/refill commands."""

    representative_ndc: str
    ncpdp_quantity_qualifier_code: str


class ServiceProvider(Model):
    """ServiceProvider model."""

    first_name: str = Field(max_length=512)
    last_name: str = Field(max_length=512)
    specialty: str = Field(max_length=512)
    practice_name: str = Field(max_length=512)
    business_fax: str | None = Field(max_length=512, default=None)
    business_phone: str | None = Field(max_length=512, default=None)
    business_address: str | None = Field(max_length=512, default=None)
    notes: str | None = Field(max_length=512, default=None)
