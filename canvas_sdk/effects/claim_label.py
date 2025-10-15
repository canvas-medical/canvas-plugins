from dataclasses import dataclass
from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect
from canvas_sdk.v1.data import Claim, TaskLabel
from canvas_sdk.v1.data.common import ColorEnum


@dataclass
class Label:
    """A class representing a label."""

    color: ColorEnum
    name: str
    position: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert the label to a dictionary."""
        return {
            "color": self.color.value,
            "name": self.name,
            "position": self.position,
        }


class AddClaimLabel(_BaseEffect):
    """Effect to add a label to a Claim."""

    class Meta:
        effect_type = EffectType.ADD_CLAIM_LABEL

    claim_id: UUID | str
    label_id: UUID | str | None = None
    label_values: Label | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The values for adding a claim label."""
        return {
            "claim_id": str(self.claim_id),
            "label_id": str(self.label_id),
            "label_values": self.label_values.to_dict() if self.label_values else None,
        }

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if self.label_values is None and self.label_id is None:
            errors.append(
                self._create_error_detail(
                    "missing",
                    "One of the fields 'label_id' or 'label_values' are required in order to add a claim label.",
                    self.label_id,
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

        if self.label_id is not None and not TaskLabel.objects.filter(id=self.label_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Label with id {self.label_id} does not exist.",
                    self.label_id,
                )
            )

        return errors


class RemoveClaimLabel(_BaseEffect):
    """Effect to remove a label from a Claim."""

    class Meta:
        effect_type = EffectType.REMOVE_CLAIM_LABEL

    claim_id: UUID | str
    label_id: UUID | str

    @property
    def values(self) -> dict[str, Any]:
        """The values for adding a claim label."""
        return {"claim_id": str(self.claim_id), "label_id": str(self.label_id)}

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

        if not TaskLabel.objects.filter(id=self.label_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Label with id {self.label_id} does not exist.",
                    self.label_id,
                )
            )

        return errors


__exports__ = (
    "Label",
    "AddClaimLabel",
    "RemoveClaimLabel",
)
