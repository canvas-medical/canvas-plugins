from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect
from canvas_sdk.v1.data import Claim, Staff, Team


class _UpdateClaimAssignee(_BaseEffect):
    """Effect to assign a claim to a staff member or a team, or clear the assignment.

    A claim is assigned to a staff member OR a team, mirroring the Task model.
    Provide at most one of ``assignee_id`` / ``team_id``; passing neither clears
    the assignment.
    """

    class Meta:
        effect_type = EffectType.UPDATE_CLAIM_ASSIGNEE

    claim_id: UUID | str
    assignee_id: str | None = None
    team_id: str | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The claim_id and the target assignee/team identifiers."""
        return {
            "claim_id": str(self.claim_id),
            "assignee_id": self.assignee_id,
            "team_id": self.team_id,
        }

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if self.assignee_id and self.team_id:
            errors.append(
                self._create_error_detail(
                    "value",
                    "A claim can be assigned to a staff member or a team, but not both.",
                    self.assignee_id,
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
        if self.assignee_id and not Staff.objects.filter(id=self.assignee_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Staff with id {self.assignee_id} does not exist.",
                    self.assignee_id,
                )
            )
        if self.team_id and not Team.objects.filter(id=self.team_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Team with id {self.team_id} does not exist.",
                    self.team_id,
                )
            )
        return errors


__exports__ = ()
