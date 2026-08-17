from typing import cast

from django.db import models

from canvas_sdk.v1.data.base import (
    AuditedModel,
    CommittableModelManager,
    CommittableQuerySet,
    IdentifiableModel,
)


class GoalLifecycleStatus(models.TextChoices):
    """GoalLifecycleStatus choices."""

    PROPOSED = "proposed", "Proposed"
    PLANNED = "planned", "Planned"
    ACCEPTED = "accepted", "Accepted"
    ACTIVE = "active", "Active"
    ON_HOLD = "on-hold", "On Hold"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"
    REJECTED = "rejected", "Rejected"


class GoalAchievementStatus(models.TextChoices):
    """GoalAchievementStatus choices."""

    IN_PROGRESS = "in-progress", "In Progress"
    IMPROVING = "improving", "Improving"
    WORSENING = "worsening", "Worsening"
    NO_CHANGE = "no-change", "No Change"
    ACHIEVED = "achieved", "Achieved"
    SUSTAINING = "sustaining", "Sustaining"
    NOT_ACHIEVED = "not-achieved", "Not Achieved"
    NO_PROGRESS = "no-progress", "No Progress"
    NOT_ATTAINABLE = "not-attainable", "Not Attainable"


class GoalPriority(models.TextChoices):
    """GoalPriority choices."""

    HIGH = "high-priority", "High Priority"
    MEDIUM = "medium-priority", "Medium Priority"
    LOW = "low-priority", "Low Priority"


class AbstractGoal(AuditedModel, IdentifiableModel):
    """AbstractGoal."""

    class Meta:
        abstract = True

    objects = cast(CommittableQuerySet, CommittableModelManager())

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="%(class)ss"
    )
    note = models.ForeignKey("v1.Note", on_delete=models.DO_NOTHING, related_name="%(class)ss")
    lifecycle_status = models.CharField(
        max_length=20,
        choices=GoalLifecycleStatus.choices,
        default=GoalLifecycleStatus.ACTIVE,
        blank=True,
    )
    achievement_status = models.CharField(
        max_length=20,
        choices=GoalAchievementStatus.choices,
        default=GoalAchievementStatus.IN_PROGRESS,
        blank=True,
    )
    priority = models.CharField(
        max_length=20, choices=GoalPriority.choices, default=GoalPriority.MEDIUM
    )
    due_date = models.DateField(null=True)
    progress = models.TextField(default="", blank=True)


class Goal(AbstractGoal):
    """Goal."""

    class Meta:
        db_table = "canvas_sdk_data_api_goal_001"

    goal_statement = models.TextField(blank=True, default="")
    start_date = models.DateField()


class UpdateGoal(AbstractGoal):
    """UpdateGoal."""

    class Meta:
        db_table = "canvas_sdk_data_api_updategoal_001"

    goal = models.ForeignKey(
        "v1.Goal", on_delete=models.DO_NOTHING, related_name="updates", null=True
    )


__exports__ = (
    "Goal",
    "UpdateGoal",
    "GoalLifecycleStatus",
    "GoalAchievementStatus",
    "GoalPriority",
)
