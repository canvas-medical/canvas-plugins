from typing import Any, Literal
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.fax.base import BaseFaxEffectRequiredRecipient
from canvas_sdk.v1.data import LabOrder


class FaxLabOrderEffect(BaseFaxEffectRequiredRecipient):
    """Fax a lab order's requisition form."""

    class Meta:
        effect_type = EffectType.FAX_LAB_ORDER

    lab_order_id: str | UUID

    def _get_error_details(self, method: Literal["apply"]) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        if self.lab_order_id and not LabOrder.objects.filter(id=self.lab_order_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Lab order with ID {self.lab_order_id} does not exist.",
                    self.lab_order_id,
                )
            )

        return errors

    @property
    def values(self) -> dict[str, Any]:
        """Return the values of the lab order fax effect."""
        return {**super().values, "lab_order_id": str(self.lab_order_id)}


__exports__ = ()
