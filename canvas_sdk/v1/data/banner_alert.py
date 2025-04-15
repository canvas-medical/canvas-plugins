from django.contrib.postgres.fields import ArrayField
from django.db import models


class BannerAlert(models.Model):
    """BannerAlert."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_banneralert_001"

    dbid = models.BigIntegerField(db_column="dbid", primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    patient = models.ForeignKey(
        "v1.Patient",
        on_delete=models.DO_NOTHING,
        related_name="banner_alerts",
        null=True,
    )
    plugin_name = models.CharField()
    key = models.CharField()
    narrative = models.CharField()
    placement = ArrayField(models.CharField())
    intent = models.CharField()
    href = models.CharField()
    status = models.CharField()


__exports__ = ("BannerAlert",)
