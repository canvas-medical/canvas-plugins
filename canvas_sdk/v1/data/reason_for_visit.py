from django.contrib.postgres.fields import ArrayField
from django.db import models


class ReasonForVisitSettingCoding(models.Model):
    """ReasonForVisitSettingCoding."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_reasonforvisitsettingcoding_001"

    objects: models.Manager["ReasonForVisitSettingCoding"]

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)

    code = models.CharField()
    display = models.CharField()
    system = models.CharField()
    version = models.CharField()

    duration = ArrayField(models.DurationField())


__exports__ = ("ReasonForVisitSettingCoding",)
