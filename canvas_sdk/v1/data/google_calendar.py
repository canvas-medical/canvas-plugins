from django.db import models

from canvas_sdk.v1.data.base import TimestampedModel


class GoogleCalendarBusyBlock(TimestampedModel):
    """A provider busy block imported from Google Calendar; blocks availability like an appointment."""

    class Meta:
        db_table = "canvas_sdk_data_api_inboundbusyhold_001"

    provider = models.ForeignKey(
        "v1.Staff", on_delete=models.DO_NOTHING, related_name="google_calendar_busy_blocks"
    )
    location = models.ForeignKey(
        "v1.PracticeLocation", on_delete=models.DO_NOTHING, related_name="+"
    )
    start_time = models.DateTimeField()
    duration_minutes = models.IntegerField()
    active = models.BooleanField()


class GoogleCalendarConnection(TimestampedModel):
    """A provider's connection to their Google account for calendar sync."""

    class Meta:
        db_table = "canvas_sdk_data_api_googlecredential_001"

    staff = models.OneToOneField(
        "v1.Staff", on_delete=models.DO_NOTHING, related_name="google_calendar_connection"
    )
    google_account_email = models.EmailField()
    needs_reconnect = models.BooleanField()


class GoogleCalendar(TimestampedModel):
    """A Google calendar on a provider's connection; selected calendars feed busy blocks."""

    class Meta:
        db_table = "canvas_sdk_data_api_staffcalendar_001"

    connection = models.ForeignKey(
        "v1.GoogleCalendarConnection", on_delete=models.DO_NOTHING, related_name="calendars"
    )
    summary = models.CharField(max_length=255)
    selected = models.BooleanField()
    is_app_created = models.BooleanField()


__exports__ = ("GoogleCalendar", "GoogleCalendarBusyBlock", "GoogleCalendarConnection")
