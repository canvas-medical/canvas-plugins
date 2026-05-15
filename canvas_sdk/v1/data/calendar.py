from typing import Self, cast

from django.db import models
from django.db.models.manager import BaseManager
from timezone_utils.fields import TimeZoneField

from canvas_sdk.v1.data.base import BaseQuerySet, IdentifiableModel


class CalendarQuerySet(BaseQuerySet):
    """A queryset for calendars."""

    def for_calendar_name(self, provider_name: str, calendar_type: str, location: str) -> Self:
        """Return a queryset that filters objects for a specific calendar name."""
        calendar_name = f"{provider_name}: {calendar_type}{f': {location}' if location else ''}"

        return self.filter(title=calendar_name)


CalendarManager = BaseManager.from_queryset(CalendarQuerySet)


class Calendar(IdentifiableModel):
    """Model to represent the Calendar."""

    class Meta:
        db_table = "canvas_sdk_data_calendars_calendar_001"

    objects = cast(CalendarQuerySet, CalendarManager())

    title = models.CharField(max_length=128)
    timezone = TimeZoneField(default="UTC")
    description = models.TextField(blank=True, null=True)


class Event(IdentifiableModel):
    """Model to represent the Calendar Event."""

    class Meta:
        db_table = "canvas_sdk_data_calendars_event_001"

    title = models.CharField(max_length=512)
    description = models.TextField(blank=True)
    calendar = models.ForeignKey("v1.Calendar", on_delete=models.CASCADE, related_name="events")
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    recurrence = models.TextField(blank=True, null=True)
    recurrence_ends_at = models.DateTimeField(blank=True, null=True)
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
    allowed_note_types = models.ManyToManyField(
        "v1.NoteType", blank=True, db_table="canvas_sdk_data_calendars_event_allowed_note_types_001"
    )


__exports__ = ("Calendar", "Event")
