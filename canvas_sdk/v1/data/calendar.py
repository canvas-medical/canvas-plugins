from typing import Self, cast

from django.db import models
from django.db.models.manager import BaseManager
from timezone_utils.fields import TimeZoneField

from canvas_sdk.v1.data.base import BaseQuerySet, Model


class CalendarQuerySet(BaseQuerySet):
    """A queryset for calendars."""

    def for_calendar_name(self, provider_name: str, calendar_type: str) -> Self:
        """Return a queryset that filters objects for a specific calendar name."""
        calendar_name = f"{provider_name}: {calendar_type}"

        return self.filter(title=calendar_name)


CalendarManager = BaseManager.from_queryset(CalendarQuerySet)


class Calendar(Model):
    """Model to represent the Calendar."""

    class Meta:
        db_table = "canvas_sdk_data_calendars_calendar_001"

    objects = cast(CalendarQuerySet, CalendarManager())

    title = models.CharField(max_length=128)
    timezone = TimeZoneField(default="UTC")
    description = models.CharField(blank=True, null=True)


__exports__ = ("Calendar",)
