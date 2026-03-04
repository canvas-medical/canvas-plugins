from dataclasses import fields
from datetime import date
from typing import Annotated, Any, ClassVar
from uuid import UUID

from pydantic import Field
from pydantic.dataclasses import dataclass
from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect
from canvas_sdk.v1.data import Claim


class _PrefixedDictMixin:
    """Mixin that converts dataclass fields to a prefixed dict, excluding None values."""

    _prefix: ClassVar[str]
    _unprefixed_fields: ClassVar[frozenset[str]] = frozenset()

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary with prefixed keys, excluding None values."""
        result = {}
        for field in fields(self):  # type: ignore[arg-type]
            f = field.name
            if (val := getattr(self, f)) is None:
                continue
            value = val.isoformat() if isinstance(val, date) else val
            key = f if f in self._unprefixed_fields else f"{self._prefix}_{f}"
            result[key] = value
        return result


@dataclass
class ClaimBillingProvider(_PrefixedDictMixin):
    """Billing provider information for a claim."""

    _prefix: ClassVar[str] = "billing_provider"
    _unprefixed_fields: ClassVar[frozenset[str]] = frozenset({"clia_number"})

    name: Annotated[str, Field(max_length=255)] | None = None
    phone: Annotated[str, Field(max_length=15)] | None = None
    addr1: Annotated[str, Field(max_length=255)] | None = None
    addr2: Annotated[str, Field(max_length=255)] | None = None
    city: Annotated[str, Field(max_length=255)] | None = None
    state: Annotated[str, Field(max_length=2)] | None = None
    zip: Annotated[str, Field(max_length=255)] | None = None
    npi: Annotated[str, Field(max_length=10)] | None = None
    tax_id: Annotated[str, Field(max_length=100)] | None = None
    tax_id_type: Annotated[str, Field(max_length=1)] | None = None
    taxonomy: Annotated[str, Field(max_length=100)] | None = None
    clia_number: Annotated[str, Field(max_length=100)] | None = None


@dataclass
class ClaimProvider(_PrefixedDictMixin):
    """Rendering or attending provider information for a claim."""

    _prefix: ClassVar[str] = "provider"

    first_name: Annotated[str, Field(max_length=255)] | None = None
    last_name: Annotated[str, Field(max_length=255)] | None = None
    middle_name: Annotated[str, Field(max_length=255)] | None = None
    npi: Annotated[str, Field(max_length=10)] | None = None
    tax_id: Annotated[str, Field(max_length=100)] | None = None
    tax_id_type: Annotated[str, Field(max_length=1)] | None = None
    taxonomy: Annotated[str, Field(max_length=100)] | None = None
    ptan_identifier: Annotated[str, Field(max_length=50)] | None = None


@dataclass
class ClaimReferringProvider(_PrefixedDictMixin):
    """Referring provider information for a claim."""

    _prefix: ClassVar[str] = "referring_provider"

    first_name: Annotated[str, Field(max_length=255)] | None = None
    last_name: Annotated[str, Field(max_length=255)] | None = None
    middle_name: Annotated[str, Field(max_length=255)] | None = None
    npi: Annotated[str, Field(max_length=10)] | None = None
    ptan_identifier: Annotated[str, Field(max_length=50)] | None = None


@dataclass
class ClaimOrderingProvider(_PrefixedDictMixin):
    """Ordering provider information for a claim."""

    _prefix: ClassVar[str] = "ordering_provider"

    first_name: Annotated[str, Field(max_length=255)] | None = None
    last_name: Annotated[str, Field(max_length=255)] | None = None
    middle_name: Annotated[str, Field(max_length=255)] | None = None
    npi: Annotated[str, Field(max_length=10)] | None = None


@dataclass
class ClaimFacility(_PrefixedDictMixin):
    """Facility information for a claim, including hospitalization dates."""

    _prefix: ClassVar[str] = "facility"
    _unprefixed_fields: ClassVar[frozenset[str]] = frozenset({"hosp_from_date", "hosp_to_date"})

    name: Annotated[str, Field(max_length=255)] | None = None
    npi: Annotated[str, Field(max_length=10)] | None = None
    addr1: Annotated[str, Field(max_length=255)] | None = None
    addr2: Annotated[str, Field(max_length=255)] | None = None
    city: Annotated[str, Field(max_length=255)] | None = None
    state: Annotated[str, Field(max_length=2)] | None = None
    zip: Annotated[str, Field(max_length=255)] | None = None
    hosp_from_date: date | None = None
    hosp_to_date: date | None = None


class _UpdateClaimProvider(_BaseEffect):
    """Effect to update a ClaimProvider."""

    class Meta:
        effect_type = EffectType.UPDATE_CLAIM_PROVIDER

    claim_id: UUID | str
    billing_provider: ClaimBillingProvider | None = None
    provider: ClaimProvider | None = None
    referring_provider: ClaimReferringProvider | None = None
    ordering_provider: ClaimOrderingProvider | None = None
    facility: ClaimFacility | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The values for updating a claim provider."""
        v = {"claim_id": str(self.claim_id)}
        for section in (
            self.billing_provider,
            self.provider,
            self.referring_provider,
            self.ordering_provider,
            self.facility,
        ):
            if section:
                v.update(section.to_dict())
        return v

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        if not (claim := Claim.objects.filter(id=self.claim_id).first()):
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Claim with id {self.claim_id} does not exist.",
                    self.claim_id,
                )
            )
            return errors
        try:
            _ = claim.provider
        except Claim.provider.RelatedObjectDoesNotExist:
            # this scenario is extremely unlikely, but in the event that a claim is manually manipulated in home-app
            # to not have any provider info, this will at least let them know there's an issue with the claim
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Claim with id {self.claim_id} does not have any existing provider information to update.",
                    self.claim_id,
                )
            )
        return errors


__exports__ = ()
