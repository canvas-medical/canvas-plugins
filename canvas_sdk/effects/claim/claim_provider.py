from datetime import date
from typing import Annotated, Any
from uuid import UUID

from pydantic import Field
from pydantic.dataclasses import dataclass
from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect
from canvas_sdk.effects.utils import _PrefixedDict
from canvas_sdk.v1.data import Claim
from canvas_sdk.v1.data import ClaimProvider as ClaimProviderModel


@dataclass
class ClaimBillingProvider(
    _PrefixedDict, prefix="billing_provider", unprefixed_fields=frozenset({"clia_number"})
):
    """Billing provider information for a claim."""

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
class ClaimProvider(_PrefixedDict, prefix="provider"):
    """Rendering or attending provider information for a claim."""

    first_name: Annotated[str, Field(max_length=255)] | None = None
    last_name: Annotated[str, Field(max_length=255)] | None = None
    middle_name: Annotated[str, Field(max_length=255)] | None = None
    npi: Annotated[str, Field(max_length=10)] | None = None
    tax_id: Annotated[str, Field(max_length=100)] | None = None
    tax_id_type: Annotated[str, Field(max_length=1)] | None = None
    taxonomy: Annotated[str, Field(max_length=100)] | None = None
    ptan_identifier: Annotated[str, Field(max_length=50)] | None = None
    addr1: Annotated[str, Field(max_length=255)] | None = None
    addr2: Annotated[str, Field(max_length=255)] | None = None
    city: Annotated[str, Field(max_length=255)] | None = None
    state: Annotated[str, Field(max_length=2)] | None = None
    zip: Annotated[str, Field(max_length=255)] | None = None


@dataclass
class ClaimReferringProvider(_PrefixedDict, prefix="referring_provider"):
    """Referring provider information for a claim."""

    first_name: Annotated[str, Field(max_length=255)] | None = None
    last_name: Annotated[str, Field(max_length=255)] | None = None
    middle_name: Annotated[str, Field(max_length=255)] | None = None
    npi: Annotated[str, Field(max_length=10)] | None = None
    ptan_identifier: Annotated[str, Field(max_length=50)] | None = None


@dataclass
class ClaimOrderingProvider(_PrefixedDict, prefix="ordering_provider"):
    """Ordering provider information for a claim."""

    first_name: Annotated[str, Field(max_length=255)] | None = None
    last_name: Annotated[str, Field(max_length=255)] | None = None
    middle_name: Annotated[str, Field(max_length=255)] | None = None
    npi: Annotated[str, Field(max_length=10)] | None = None


@dataclass
class ClaimFacility(
    _PrefixedDict,
    prefix="facility",
    unprefixed_fields=frozenset({"hosp_from_date", "hosp_to_date"}),
):
    """Facility information for a claim, including hospitalization dates."""

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
        if not ClaimProviderModel.objects.filter(claim=claim).exists():
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
