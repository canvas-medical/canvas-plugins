from django.db import models

from canvas_sdk.v1.data.base import TimestampedModel


class ScheduleDuration(TimestampedModel):
    """A duration that can be used with appointments or schedule events."""

    class Meta:
        db_table = "canvas_sdk_data_api_scheduleduration_001"

    duration = models.DurationField(unique=True)
    is_appointment_duration_option = models.BooleanField(default=True)


__exports__ = ("ScheduleDuration",)
