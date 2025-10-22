from collections.abc import Sequence
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


class _ClaimLabelBase(_BaseEffect):
    """Base class for managing ClaimLabels."""

    claim_id: UUID | str
    labels: Sequence[str | Label]

    @property
    def _existing_label_names(self) -> list[str]:
        return [label for label in self.labels if type(label) is str]

    @property
    def _new_label_values(self) -> list[Label]:
        return [label for label in self.labels if type(label) is Label]

    def _check_if_named_labels_exist(self) -> list[InitErrorDetails]:
        requested_label_names = self._existing_label_names
        existing_labels = TaskLabel.objects.filter(name__in=requested_label_names).values_list(
            "name", flat=True
        )
        missing_labels = set(requested_label_names) - set(existing_labels)
        if len(missing_labels) == 0:
            return []
        missing_labels_list = sorted(missing_labels)
        missing_labels_text = ", ".join(missing_labels_list)
        has_multiple = len(missing_labels_list) > 1
        plural = "s" if has_multiple else ""
        do = "do" if has_multiple else "does"
        message = f"Label{plural} with name{plural} {missing_labels_text} {do} not exist."
        return [self._create_error_detail("value", message, missing_labels_text)]

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
        errors.extend(self._check_if_claim_exists())
        errors.extend(self._check_if_named_labels_exist())
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
            "labels": self._existing_label_names,
            "label_values": [label_value.to_dict() for label_value in self._new_label_values],
        }


class RemoveClaimLabel(_ClaimLabelBase):
    """Effect to remove a label from a Claim."""

    class Meta:
        effect_type = EffectType.REMOVE_CLAIM_LABEL

    labels: list[str]

    @property
    def values(self) -> dict[str, Any]:
        """The values for adding a claim label."""
        return {"claim_id": str(self.claim_id), "labels": self.labels}


__exports__ = (
    "Label",
    "AddClaimLabel",
    "RemoveClaimLabel",
)
