from typing import Any
from uuid import UUID

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect
from canvas_sdk.v1.data import RefillRequest, Staff


class UpdateRefillRequest(_BaseEffect):
    """
    An Effect that will update a refill request.
    """

    class Meta:
        effect_type = EffectType.UPDATE_REFILL_REQUEST

    id: UUID = Field(strict=False)
    assignee_id: str = Field(min_length=1)

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if self.id and not RefillRequest.objects.filter(id=self.id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Refill request with id '{self.id}' does not exist.",
                    self.id,
                )
            )

        if self.assignee_id and not Staff.objects.filter(id=self.assignee_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Staff with id '{self.assignee_id}' does not exist.",
                    self.assignee_id,
                )
            )

        return errors

    @property
    def values(self) -> dict[str, Any]:
        """The values for updating a refill request."""
        return {
            "id": str(self.id),
            "assignee_id": self.assignee_id,
        }


__exports__ = ("UpdateRefillRequest",)
