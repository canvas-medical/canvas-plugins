from typing import Any
from uuid import UUID

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect
from canvas_sdk.v1.data import RefillRequest, Staff


class UpdateRefillRequest(_BaseEffect):
    """
    An Effect that will update a refill request in the refill queue.

    Sets the assignee, ignores the request (the same as the Ignore button in the
    refill panel), or both. Only pending requests (see RefillRequest.objects.pending())
    can be updated. Ignoring sends nothing to the pharmacy.
    """

    class Meta:
        effect_type = EffectType.UPDATE_REFILL_REQUEST

    id: UUID = Field(strict=False)
    assignee_id: str | None = Field(default=None, min_length=1)
    ignored: bool | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if self.assignee_id is None and self.ignored is None:
            errors.append(
                self._create_error_detail(
                    "missing",
                    "At least one of 'assignee_id' or 'ignored' must be set.",
                    None,
                )
            )

        if self.ignored is False:
            errors.append(
                self._create_error_detail(
                    "value",
                    "Un-ignoring a refill request is not supported.",
                    self.ignored,
                )
            )

        if self.id and not RefillRequest.objects.pending().filter(id=self.id).exists():
            if RefillRequest.objects.filter(id=self.id).exists():
                message = (
                    f"Refill request with id '{self.id}' is not pending: "
                    "it was already ignored or answered."
                )
            else:
                message = f"Refill request with id '{self.id}' does not exist."
            errors.append(self._create_error_detail("value", message, self.id))

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
            "ignored": self.ignored,
        }


__exports__ = ("UpdateRefillRequest",)
