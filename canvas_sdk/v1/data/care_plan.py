from django.db import models

from canvas_sdk.v1.data.base import (
    BaseQuerySet,
    ForPatientQuerySetMixin,
    IdentifiableModel,
    TimestampedModel,
)
from canvas_sdk.v1.data.coding import Coding


class CarePlanStatus(models.TextChoices):
    """Status choices for CarePlan."""

    DRAFT = "draft", "Draft"
    ACTIVE = "active", "Active"
    ON_HOLD = "on-hold", "On Hold"
    REVOKED = "revoked", "Revoked"
    COMPLETED = "completed", "Completed"
    ENTERED_IN_ERROR = "entered-in-error", "Entered in Error"
    UNKNOWN = "unknown", "Unknown"


class CarePlanIntent(models.TextChoices):
    """Intent choices for CarePlan."""

    PROPOSAL = "proposal", "Proposal"
    PLAN = "plan", "Plan"
    ORDER = "order", "Order"
    OPTION = "option", "Option"


class CarePlanCoding(Coding):
    """A category coding referenced by CarePlan.category."""

    class Meta:
        db_table = "canvas_sdk_data_api_careplancoding_001"


class CarePlanQuerySet(ForPatientQuerySetMixin, BaseQuerySet):
    """QuerySet for CarePlan."""


class CarePlan(TimestampedModel, IdentifiableModel):
    """A patient's care plan, served over FHIR as CarePlan."""

    class Meta:
        db_table = "canvas_sdk_data_api_careplan_001"

    objects = CarePlanQuerySet.as_manager()

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="care_plans"
    )
    originator = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, related_name="+")
    status = models.CharField(
        choices=CarePlanStatus.choices, max_length=16, default=CarePlanStatus.ACTIVE
    )
    intent = models.CharField(
        choices=CarePlanIntent.choices, max_length=8, default=CarePlanIntent.PLAN
    )
    category = models.ForeignKey(
        CarePlanCoding, on_delete=models.DO_NOTHING, null=True, related_name="care_plans"
    )

    def __str__(self) -> str:
        return f"CarePlan(id={self.id})"


__exports__ = (
    "CarePlan",
    "CarePlanCoding",
    "CarePlanIntent",
    "CarePlanStatus",
)
