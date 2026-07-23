from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel


class ScheduleDuration(TimestampedModel, IdentifiableModel):
    """An allowed appointment duration (in minutes)."""

    class Meta:
        db_table = "canvas_sdk_data_api_scheduleduration_001"

    minutes = models.IntegerField()
    label = models.CharField(max_length=64, blank=True, default="")
    active = models.BooleanField(default=True)


__exports__ = ("ScheduleDuration",)
