from dataclasses import dataclass
from typing import Any
from uuid import UUID

from pydantic import conlist
from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect
from canvas_sdk.v1.data import Claim
from canvas_sdk.v1.data.common import ColorEnum


@dataclass
class Label:
    """A class representing a label."""

    color: ColorEnum
    name: str

    def to_dict(self) -> dict[str, Any]:
        """Convert the label to a dictionary."""
        return {"color": self.color.value, "name": self.name}


class _ClaimLabelBase(_BaseEffect):
    """Base class for managing ClaimLabels."""

    claim_id: UUID | str
    labels: conlist(str | Label, min_length=1)  # type: ignore

    def _check_if_claim_exists(self) -> list[InitErrorDetails]:
        if Claim.objects.filter(id=self.claim_id).exists():
            return []
        return [
            (
                self._create_error_detail(
                    "value",
                    f"Claim with id {self.claim_id} does not exist.",
                    self.claim_id,
                )
            )
        ]

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


class AddClaimLabel(_ClaimLabelBase):
    """Effect to add a label to a Claim."""

    class Meta:
        effect_type = EffectType.ADD_CLAIM_LABEL

    @property
    def values(self) -> dict[str, Any]:
        """The values for adding a claim label."""
        return {
            "claim_id": str(self.claim_id),
            "labels": [
                label.to_dict() if isinstance(label, Label) else {"name": label}
                for label in self.labels
            ],
        }


class RemoveClaimLabel(_ClaimLabelBase):
    """Effect to remove a label from a Claim."""

    class Meta:
        effect_type = EffectType.REMOVE_CLAIM_LABEL

    labels: conlist(str, min_length=1)  # type: ignore

    @property
    def values(self) -> dict[str, Any]:
        """The values for removing a claim label."""
        return {"claim_id": str(self.claim_id), "labels": list(self.labels)}


__exports__ = (
    "Label",
    "AddClaimLabel",
    "RemoveClaimLabel",
)
