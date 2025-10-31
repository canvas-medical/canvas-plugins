from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel


class Event(IdentifiableModel):
    """Model to represent the Calendar Event."""

    class Meta:
        db_table = "canvas_sdk_data_calendars_event_001"

    title = models.CharField(max_length=128)
    description = models.CharField(blank=True, null=True)
    calendar = models.ForeignKey("v1.Calendar", on_delete=models.CASCADE, related_name="events")
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    recurrence = models.CharField(
        blank=True, null=True
    )  # TODO: Change to proper recurrence field/type?
    recurrence_ends_at = models.DateTimeField()
    recurring_parent_event = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="exceptions",
    )
    original_starts_at = models.DateTimeField(blank=True, null=True)
    is_all_day = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)


__exports__ = ("Event",)
