from typing import Annotated, Any
from uuid import UUID

from pydantic import Field, TypeAdapter
from pydantic.dataclasses import dataclass
from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect
from canvas_sdk.v1.data import Claim, Staff


@dataclass
class ClaimSupervisingProvider:
    """Free-text supervising provider snapshot for a claim."""

    first_name: Annotated[str, Field(max_length=255)] | None = None
    last_name: Annotated[str, Field(max_length=255)] | None = None
    middle_name: Annotated[str, Field(max_length=255)] | None = None
    npi: Annotated[str, Field(max_length=10)] | None = None
    taxonomy: Annotated[str, Field(max_length=100)] | None = None
    tax_id: Annotated[str, Field(max_length=100)] | None = None
    tax_id_type: Annotated[str, Field(max_length=1)] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary, excluding None values."""
        return TypeAdapter(type(self)).dump_python(self, mode="json", exclude_none=True)


class _UpdateClaimSupervisingProvider(_BaseEffect):
    """Effect to set or update a claim's supervising provider snapshot.

    Supports exactly one of two modes:

    * ``staff_id`` — snapshot is populated from the Staff record (name, NPI,
      taxonomy, tax id) by the interpreter and remains linked to that Staff.
    * ``supervising_provider`` — a free-text override; the snapshot fields are
      written directly and the Staff association is cleared.
    """

    class Meta:
        effect_type = EffectType.UPDATE_CLAIM_SUPERVISING_PROVIDER

    claim_id: UUID | str
    staff_id: str | None = None
    supervising_provider: ClaimSupervisingProvider | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The values for updating a claim's supervising provider snapshot."""
        v: dict[str, Any] = {"claim_id": str(self.claim_id)}
        if self.staff_id:
            v["staff_id"] = self.staff_id
        elif self.supervising_provider:
            v.update(self.supervising_provider.to_dict())
        return v

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if bool(self.staff_id) == bool(self.supervising_provider):
            errors.append(
                self._create_error_detail(
                    "value",
                    "Exactly one of 'staff_id' or 'supervising_provider' must be provided.",
                    self.staff_id,
                )
            )

        if not Claim.objects.filter(id=self.claim_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Claim with id {self.claim_id} does not exist.",
                    self.claim_id,
                )
            )

        if self.staff_id and not Staff.objects.filter(id=self.staff_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Staff with id {self.staff_id} does not exist.",
                    self.staff_id,
                )
            )

        return errors


class _SetClaimIncidentTo(_BaseEffect):
    """Effect to toggle a claim's incident_to billing flag."""

    class Meta:
        effect_type = EffectType.SET_CLAIM_INCIDENT_TO

    claim_id: UUID | str
    incident_to: bool

    @property
    def values(self) -> dict[str, Any]:
        """The values for setting a claim's incident_to flag."""
        return {"claim_id": str(self.claim_id), "incident_to": self.incident_to}

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        if not Claim.objects.filter(id=self.claim_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Claim with id {self.claim_id} does not exist.",
                    self.claim_id,
                )
            )
        return errors


__exports__ = ("ClaimSupervisingProvider",)
