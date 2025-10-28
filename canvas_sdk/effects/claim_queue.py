from typing import Any
from uuid import UUID

from pydantic import constr
from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect
from canvas_sdk.v1.data import Claim, ClaimQueue


class MoveClaimToQueue(_BaseEffect):
    """
    An Effect that moves a Claim to a Queue.
    """

    class Meta:
        effect_type = EffectType.MOVE_CLAIM_TO_QUEUE

    claim_id: UUID | str
    queue: constr(min_length=1, strip_whitespace=True)  # type: ignore[valid-type]

    @property
    def values(self) -> dict[str, Any]:
        """The claim_id and queue_id."""
        return {"claim_id": str(self.claim_id), "queue": self.queue}

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if not Claim.objects.filter(id=self.claim_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    "Claim does not exist",
                    self.claim_id,
                )
            )
        if not ClaimQueue.objects.filter(name=self.queue).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    "Queue does not exist",
                    self.queue,
                )
            )
        return errors


__exports__ = ("MoveClaimToQueue",)
