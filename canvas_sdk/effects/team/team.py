import json
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.effects import Effect


class TeamResponsibility(StrEnum):
    """Active + organizational responsibilities a Team can be tagged with."""

    COMMUNICATE_DIAGNOSTIC_RESULTS_TO_PATIENT = "COMMUNICATE_DIAGNOSTIC_RESULTS_TO_PATIENT"
    COORDINATE_REFERRALS_FOR_PATIENT = "COORDINATE_REFERRALS_FOR_PATIENT"
    PROCESS_REFILL_REQUESTS = "PROCESS_REFILL_REQUESTS"
    PROCESS_CHANGE_REQUESTS = "PROCESS_CHANGE_REQUESTS"
    POPULATION_HEALTH_CAMPAIGN_OUTREACH = "POPULATION_HEALTH_CAMPAIGN_OUTREACH"
    COLLECT_PATIENT_PAYMENTS = "COLLECT_PATIENT_PAYMENTS"
    COMPLETE_OPEN_LAB_ORDERS = "COMPLETE_OPEN_LAB_ORDERS"
    REVIEW_ERA_POSTING_EXCEPTIONS = "REVIEW_ERA_POSTING_EXCEPTIONS"
    REVIEW_COVERAGES = "REVIEW_COVERAGES"
    COLLECT_SPECIMENS_FROM_PATIENT = "COLLECT_SPECIMENS_FROM_PATIENT"
    SCHEDULE_LAB_VISITS_FOR_PATIENT = "SCHEDULE_LAB_VISITS_FOR_PATIENT"


class Team(TrackableFieldsModel):
    """Effect to create, update, or delete a Team."""

    class Meta:
        effect_type = "TEAM"

    id: str | UUID | None = None
    name: str | None = None
    responsibilities: list[TeamResponsibility] | None = None
    phone: str | None = None
    fax: str | None = None
    email: str | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        if method == "create" and not self.name:
            errors.append(
                self._create_error_detail(
                    "missing",
                    "Field 'name' is required to create a team.",
                    self.name,
                )
            )
        if method in ("update", "delete") and not self.id:
            errors.append(
                self._create_error_detail(
                    "missing",
                    f"Field 'id' is required to {method} a team.",
                    self.id,
                )
            )
        return errors

    def create(self) -> Effect:
        """Build the CREATE effect."""
        self._validate_before_effect("create")
        return Effect(
            type=f"CREATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )

    def update(self) -> Effect:
        """Build the UPDATE effect."""
        self._validate_before_effect("update")
        return Effect(
            type=f"UPDATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )

    def delete(self) -> Effect:
        """Build the DELETE effect (carries only the id)."""
        self._validate_before_effect("delete")
        return Effect(
            type=f"DELETE_{self.Meta.effect_type}",
            payload=json.dumps({"data": {"id": str(self.id)}}),
        )


class TeamMember(TrackableFieldsModel):
    """Effect to add or remove a staff member from a Team."""

    class Meta:
        effect_type = "TEAM_MEMBER"

    team_id: str | UUID | None = None
    staff_id: str | UUID | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        if method in ("assign", "remove"):
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
        """Build the ASSIGN effect (attach the relation)."""
        self._validate_before_effect("assign")
        return Effect(
            type=f"ASSIGN_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )

    def remove(self) -> Effect:
        """Build the REMOVE effect (detach the relation)."""
        self._validate_before_effect("remove")
        return Effect(
            type=f"REMOVE_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )


__exports__ = ("Team", "TeamMember", "TeamResponsibility")
