from django.db import models

from canvas_sdk.v1.data.base import AuditedModel, IdentifiableModel


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


class Goal(AuditedModel, IdentifiableModel):
    """Goal."""

    class Meta:
        db_table = "canvas_sdk_data_api_goal_001"

    patient = models.ForeignKey("v1.Patient", on_delete=models.DO_NOTHING, related_name="goals")
    note = models.ForeignKey("v1.Note", on_delete=models.DO_NOTHING, related_name="goals")
    lifecycle_status = models.CharField(max_length=20, choices=GoalLifecycleStatus.choices)
    achievement_status = models.CharField(max_length=20, choices=GoalAchievementStatus.choices)
    priority = models.CharField(max_length=20, choices=GoalPriority.choices)
    due_date = models.DateField()
    progress = models.TextField()
    goal_statement = models.TextField()
    start_date = models.DateField()


__exports__ = ("Goal", "GoalLifecycleStatus", "GoalAchievementStatus", "GoalPriority")
