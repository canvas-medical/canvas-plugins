from dataclasses import asdict, dataclass
from datetime import date
from typing import Any
from uuid import UUID

from pydantic import constr
from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect
from canvas_sdk.v1.data import Claim


@dataclass
class ClaimBillingProvider:
    """Billing provider information for a claim."""

    name: constr(max_length=255) | None = None  # type: ignore[valid-type]
    phone: constr(max_length=15) | None = None  # type: ignore[valid-type]
    addr1: constr(max_length=255) | None = None  # type: ignore[valid-type]
    addr2: constr(max_length=255) | None = None  # type: ignore[valid-type]
    city: constr(max_length=255) | None = None  # type: ignore[valid-type]
    state: constr(max_length=2) | None = None  # type: ignore[valid-type]
    zip: constr(max_length=255) | None = None  # type: ignore[valid-type]
    id: constr(max_length=255) | None = None  # type: ignore[valid-type]
    npi: constr(max_length=10) | None = None  # type: ignore[valid-type]
    tax_id: constr(max_length=100) | None = None  # type: ignore[valid-type]
    tax_id_type: constr(max_length=1) | None = None  # type: ignore[valid-type]
    taxonomy: constr(max_length=100) | None = None  # type: ignore[valid-type]

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary, excluding None values."""
        return {f"billing_provider_{k}": v for k, v in asdict(self).items() if v is not None}


@dataclass
class ClaimProvider:
    """Rendering or attending provider information for a claim."""

    id: constr(max_length=255) | None = None  # type: ignore[valid-type]
    first_name: constr(max_length=255) | None = None  # type: ignore[valid-type]
    last_name: constr(max_length=255) | None = None  # type: ignore[valid-type]
    middle_name: constr(max_length=255) | None = None  # type: ignore[valid-type]
    npi: constr(max_length=10) | None = None  # type: ignore[valid-type]
    tax_id: constr(max_length=100) | None = None  # type: ignore[valid-type]
    tax_id_type: constr(max_length=1) | None = None  # type: ignore[valid-type]
    taxonomy: constr(max_length=100) | None = None  # type: ignore[valid-type]
    ptan_identifier: constr(max_length=50) | None = None  # type: ignore[valid-type]

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary, excluding None values."""
        return {f"provider_{k}": v for k, v in asdict(self).items() if v is not None}


@dataclass
class ClaimReferringProvider:
    """Referring provider information for a claim."""

    id: constr(max_length=255) | None = None  # type: ignore[valid-type]
    first_name: constr(max_length=255) | None = None  # type: ignore[valid-type]
    last_name: constr(max_length=255) | None = None  # type: ignore[valid-type]
    middle_name: constr(max_length=255) | None = None  # type: ignore[valid-type]
    npi: constr(max_length=10) | None = None  # type: ignore[valid-type]
    ptan_identifier: constr(max_length=50) | None = None  # type: ignore[valid-type]

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary, excluding None values."""
        return {f"referring_provider_{k}": v for k, v in asdict(self).items() if v is not None}


@dataclass
class ClaimOrderingProvider:
    """Ordering provider information for a claim."""

    first_name: constr(max_length=255) | None = None  # type: ignore[valid-type]
    last_name: constr(max_length=255) | None = None  # type: ignore[valid-type]
    middle_name: constr(max_length=255) | None = None  # type: ignore[valid-type]
    npi: constr(max_length=10) | None = None  # type: ignore[valid-type]

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary, excluding None values."""
        return {f"ordering_provider_{k}": v for k, v in asdict(self).items() if v is not None}


@dataclass
class ClaimFacility:
    """Facility information for a claim, including hospitalization dates."""

    id: constr(max_length=255) | None = None  # type: ignore[valid-type]
    name: constr(max_length=255) | None = None  # type: ignore[valid-type]
    npi: constr(max_length=10) | None = None  # type: ignore[valid-type]
    addr1: constr(max_length=255) | None = None  # type: ignore[valid-type]
    addr2: constr(max_length=255) | None = None  # type: ignore[valid-type]
    city: constr(max_length=255) | None = None  # type: ignore[valid-type]
    state: constr(max_length=2) | None = None  # type: ignore[valid-type]
    zip: constr(max_length=255) | None = None  # type: ignore[valid-type]
    hosp_from_date: date | None = None
    hosp_to_date: date | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary, excluding None values."""
        result = {
            f"facility_{k}": v
            for k, v in asdict(self).items()
            if v is not None and k not in ("hosp_from_date", "hosp_to_date")
        }
        if self.hosp_from_date is not None:
            result["hosp_from_date"] = self.hosp_from_date.isoformat()
        if self.hosp_to_date is not None:
            result["hosp_to_date"] = self.hosp_to_date.isoformat()
        return result


class _UpdateClaimProvider(_BaseEffect):
    """Effect to update a ClaimProvider."""

    class Meta:
        effect_type = EffectType.UPDATE_CLAIM_PROVIDER

    claim_id: UUID | str
    clia_number: constr(max_length=100) | None = None  # type: ignore[valid-type]
    billing_provider: ClaimBillingProvider | None = None
    provider: ClaimProvider | None = None
    referring_provider: ClaimReferringProvider | None = None
    ordering_provider: ClaimOrderingProvider | None = None
    facility: ClaimFacility | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The values for updating a claim provider."""
        v = {"claim_id": str(self.claim_id)}
        if self.clia_number:
            v["clia_number"] = self.clia_number
        for section in (
            self.billing_provider,
            self.provider,
            self.referring_provider,
            self.ordering_provider,
            self.facility,
        ):
            if section:
                v = v | section.to_dict()
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
        if not claim.provider:
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
