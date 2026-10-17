import json
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.effects import Effect
from canvas_sdk.effects._config_crud import ConfigCrudEffect


class TeamResponsibility(StrEnum):
    """Work a Team can be responsible for."""

    COLLECT_SPECIMENS_FROM_PATIENT = "COLLECT_SPECIMENS_FROM_PATIENT"
    COMMUNICATE_DIAGNOSTIC_RESULTS_TO_PATIENT = "COMMUNICATE_DIAGNOSTIC_RESULTS_TO_PATIENT"
    COORDINATE_REFERRALS_FOR_PATIENT = "COORDINATE_REFERRALS_FOR_PATIENT"
    PROCESS_REFILL_REQUESTS = "PROCESS_REFILL_REQUESTS"
    PROCESS_CHANGE_REQUESTS = "PROCESS_CHANGE_REQUESTS"
    SCHEDULE_LAB_VISITS_FOR_PATIENT = "SCHEDULE_LAB_VISITS_FOR_PATIENT"
    POPULATION_HEALTH_CAMPAIGN_OUTREACH = "POPULATION_HEALTH_CAMPAIGN_OUTREACH"
    COLLECT_PATIENT_PAYMENTS = "COLLECT_PATIENT_PAYMENTS"
    COMPLETE_OPEN_LAB_ORDERS = "COMPLETE_OPEN_LAB_ORDERS"
    REVIEW_ERA_POSTING_EXCEPTIONS = "REVIEW_ERA_POSTING_EXCEPTIONS"
    REVIEW_COVERAGES = "REVIEW_COVERAGES"


class Team(ConfigCrudEffect):
    """Create, update, or delete a Team. ``id`` is the team's id."""

    class Meta:
        effect_type = "TEAM"

    _entity_label: str = "team"
    _create_required: tuple[str, ...] = ("name",)

    name: str | None = None
    responsibilities: list[TeamResponsibility] | None = None


class TeamMember(TrackableFieldsModel):
    """Add a staff member to a Team or remove one.

    ``team_id`` is the team's id and ``staff_id`` the staff member's id.
    """

    class Meta:
        effect_type = "TEAM_MEMBER"

    team_id: str | UUID | None = None
    staff_id: str | None = None

    @property
    def values(self) -> dict[str, Any]:
        """Serialize ids as strings."""
        return {"team_id": str(self.team_id), "staff_id": str(self.staff_id)}

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        for required in ("team_id", "staff_id"):
            if not getattr(self, required):
                errors.append(
                    self._create_error_detail(
                        "missing",
                        f"Field '{required}' is required to {method} a team member.",
                        getattr(self, required),
                    )
                )
        return errors

    def assign(self) -> Effect:
        """Build the ASSIGN effect."""
        self._validate_before_effect("assign")
        return Effect(
            type=f"ASSIGN_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )

    def remove(self) -> Effect:
        """Build the REMOVE effect."""
        self._validate_before_effect("remove")
        return Effect(
            type=f"REMOVE_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )


__exports__ = ("Team", "TeamMember", "TeamResponsibility")
