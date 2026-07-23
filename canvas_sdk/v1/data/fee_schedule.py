from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel


class FeeSchedule(TimestampedModel, IdentifiableModel):
    """A line-item entry in the customer's fee schedule (code + price)."""

    class Meta:
        db_table = "canvas_sdk_data_api_feeschedule_001"

    code = models.CharField(max_length=32)
    code_system = models.CharField(max_length=64, blank=True, default="")
    description = models.CharField(max_length=512, blank=True, default="")
    price = models.DecimalField(max_digits=12, decimal_places=2)
    modifier = models.CharField(max_length=16, blank=True, default="")
    active = models.BooleanField(default=True)


__exports__ = ("FeeSchedule",)
