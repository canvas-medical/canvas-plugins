from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel


class PostingRule(TimestampedModel, IdentifiableModel):
    """An ERA-posting automation rule (conditions + action)."""

    class Meta:
        db_table = "canvas_sdk_data_api_postingrule_001"

    name = models.CharField(max_length=255)
    description = models.CharField(max_length=512, blank=True, default="")
    action = models.CharField(max_length=64)
    conditions = models.JSONField(null=True, blank=True)
    priority = models.IntegerField(default=0)
    active = models.BooleanField(default=True)


__exports__ = ("PostingRule",)
