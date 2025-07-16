from django.contrib.postgres.fields import ArrayField
from django.db import models

from canvas_sdk.v1.data.base import Model


class BannerAlert(Model):
    """BannerAlert."""

    class Meta:
        db_table = "canvas_sdk_data_api_banneralert_001"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    patient = models.ForeignKey(
        "v1.Patient",
        on_delete=models.DO_NOTHING,
        related_name="banner_alerts",
        null=True,
    )
    plugin_name = models.CharField(max_length=256)
    key = models.CharField(max_length=255)
    narrative = models.CharField(max_length=90)
    placement = ArrayField(models.CharField(max_length=64))
    intent = models.CharField(max_length=64)
    href = models.CharField(max_length=255)
    status = models.CharField(max_length=64)


__exports__ = ("BannerAlert",)
