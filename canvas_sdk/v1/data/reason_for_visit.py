from django.contrib.postgres.fields import ArrayField
from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel


class ReasonForVisitSettingCoding(IdentifiableModel):
    """ReasonForVisitSettingCoding."""

    class Meta:
        db_table = "canvas_sdk_data_api_reasonforvisitsettingcoding_001"

    objects: models.Manager["ReasonForVisitSettingCoding"]

    code = models.CharField(max_length=255)
    display = models.CharField(max_length=1000)
    system = models.CharField(max_length=255)
    version = models.CharField(max_length=255)

    duration = ArrayField(models.DurationField())


__exports__ = ("ReasonForVisitSettingCoding",)
