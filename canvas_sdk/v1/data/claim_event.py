from django.db import models

from canvas_sdk.v1.data.base import TimestampedModel


class ClaimCoverageEventType(models.TextChoices):
    """What happened to a claim coverage."""

    ACTIVATE = "activate", "Activate"
    DEACTIVATED = "deactivated", "Deactivate"
    CURRENT = "current", "Current"
    REORDER = "reorder", "Reordered"
    EDIT = "edit", "Edited"


class ClaimSnoozeState(models.TextChoices):
    """Whether a snooze was set, cleared, or expired."""

    EXPIRE = "expire", "expire"
    CLEAR = "clear", "clear"
    SET = "set", "set"


class ClaimStateChangeEvent(TimestampedModel):
    """A claim leaving one queue and entering another."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_claimstatechangeevent_001"

    claim = models.ForeignKey(
        "v1.Claim", on_delete=models.CASCADE, related_name="claim_state_change_events"
    )
    queue_entered = models.ForeignKey(
        "v1.ClaimQueue", on_delete=models.CASCADE, related_name="enter_events", null=True
    )
    queue_exited = models.ForeignKey(
        "v1.ClaimQueue", on_delete=models.CASCADE, related_name="exit_events", null=True
    )
    originator = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.CASCADE, related_name="+", null=True
    )


class ClaimCoverageEvent(TimestampedModel):
    """A change to one of a claim's coverages."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_claimcoverageevent_001"

    claim = models.ForeignKey(
        "v1.Claim", on_delete=models.CASCADE, related_name="claim_coverage_events"
    )
    event_type = models.CharField(choices=ClaimCoverageEventType.choices, max_length=12)
    originator = models.ForeignKey("v1.CanvasUser", on_delete=models.PROTECT, related_name="+")
    claim_coverage = models.ForeignKey(
        "v1.ClaimCoverage", on_delete=models.PROTECT, related_name="events"
    )


class ClaimAssigneeEvent(TimestampedModel):
    """A change to who owns a claim: a staff member, a team, or nobody (both empty)."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_claimassigneeevent_001"

    claim = models.ForeignKey("v1.Claim", on_delete=models.CASCADE, related_name="assignee_events")
    assignee = models.ForeignKey("v1.Staff", on_delete=models.SET_NULL, related_name="+", null=True)
    team = models.ForeignKey("v1.Team", on_delete=models.SET_NULL, related_name="+", null=True)
    # The owner's name when the change was made, kept after the staff member or team is deleted.
    assignee_name = models.CharField(max_length=255, blank=True, default="")
    team_name = models.CharField(max_length=255, blank=True, default="")
    # Empty when a plugin made the change.
    originator = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.PROTECT, related_name="+", null=True
    )


class ClaimSnoozeEvent(TimestampedModel):
    """A claim snooze being set, cleared, or expiring."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_claimsnoozeevent_001"

    claim = models.ForeignKey("v1.Claim", on_delete=models.CASCADE, related_name="snooze_events")
    state = models.CharField(choices=ClaimSnoozeState.choices, max_length=12)
    date = models.DateField(null=True, blank=True)
    originator = models.ForeignKey("v1.CanvasUser", on_delete=models.PROTECT, related_name="+")


__exports__ = (
    "ClaimAssigneeEvent",
    "ClaimCoverageEvent",
    "ClaimCoverageEventType",
    "ClaimSnoozeEvent",
    "ClaimSnoozeState",
    "ClaimStateChangeEvent",
)
