from typing import Any, Literal
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.fax.base import BaseFaxEffectOptionalRecipient
from canvas_sdk.v1.data import ImagingOrder


class FaxImagingOrderEffect(BaseFaxEffectOptionalRecipient):
    """Fax an imaging order, by default to its imaging center."""

    class Meta:
        effect_type = EffectType.FAX_IMAGING_ORDER

    imaging_order_id: str | UUID

    def _get_error_details(self, method: Literal["apply"]) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        if (
            self.imaging_order_id
            and not ImagingOrder.objects.filter(id=self.imaging_order_id).exists()
        ):
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Imaging order with ID {self.imaging_order_id} does not exist.",
                    self.imaging_order_id,
                )
            )

        return errors

    @property
    def values(self) -> dict[str, Any]:
        """Return the values of the imaging order fax effect."""
        return {**super().values, "imaging_order_id": str(self.imaging_order_id)}


__exports__ = ()
