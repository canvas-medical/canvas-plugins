from django.db import models

from canvas_sdk.v1.data.base import TimestampedModel
from canvas_sdk.v1.data.organization import Organization


class OrganizationSetting(TimestampedModel):
    """A named runtime setting attached to the Organization (single-record)."""

    class Meta:
        db_table = "canvas_sdk_data_api_organizationsetting_001"

    organization = models.ForeignKey(
        Organization,
        on_delete=models.DO_NOTHING,
        related_name="settings",
    )
    name = models.CharField(max_length=255)
    value = models.JSONField(null=True, blank=True)
    description = models.CharField(max_length=512, blank=True, default="")


__exports__ = ("OrganizationSetting",)
