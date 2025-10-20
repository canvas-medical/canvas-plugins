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
    labels: list[str] | None = None

    def _check_if_all_labels_exist(self) -> list[InitErrorDetails]:
        if self.labels is not None:
            existing_labels = TaskLabel.objects.filter(name__in=self.labels).values_list(
                "name", flat=True
            )
            missing_labels = set(self.labels) - set(existing_labels)
            if len(missing_labels) > 0:
                missing_labels_list = sorted(missing_labels)
                missing_labels_text = ", ".join(missing_labels_list)
                has_multiple = len(missing_labels_list) > 1
                plural = "s" if has_multiple else ""
                do = "do" if has_multiple else "does"
                message = f"Label{plural} with name{plural} {missing_labels_text} {do} not exist."
                return [self._create_error_detail("value", message, missing_labels_text)]
        return []

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


class AddClaimLabel(_ClaimLabelBase):
    """Effect to add a label to a Claim."""

    class Meta:
        effect_type = EffectType.ADD_CLAIM_LABEL

    label_values: list[Label] | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The values for adding a claim label."""
        return {
            "claim_id": str(self.claim_id),
            "labels": self.labels,
            "label_values": [label_value.to_dict() for label_value in self.label_values]
            if self.label_values
            else None,
        }

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if self.label_values is None and self.labels is None:
            errors.append(
                self._create_error_detail(
                    "missing",
                    "One of the fields 'labels' or 'label_values' are required in order to add a claim label.",
                    self.labels,
                )
            )
        errors.extend(self._check_if_claim_exists())
        errors.extend(self._check_if_all_labels_exist())

        return errors


class RemoveClaimLabel(_ClaimLabelBase):
    """Effect to remove a label from a Claim."""

    class Meta:
        effect_type = EffectType.REMOVE_CLAIM_LABEL

    labels: list[str]

    @property
    def values(self) -> dict[str, Any]:
        """The values for adding a claim label."""
        return {"claim_id": str(self.claim_id), "labels": self.labels}

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        errors.extend(self._check_if_claim_exists())
        errors.extend(self._check_if_all_labels_exist())
        return errors


__exports__ = (
    "Label",
    "AddClaimLabel",
    "RemoveClaimLabel",
)
