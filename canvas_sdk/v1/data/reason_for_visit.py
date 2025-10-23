from django.contrib.postgres.fields import ArrayField
from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel
from canvas_sdk.v1.data.coding import Coding


class ReasonForVisitSettingCoding(IdentifiableModel, Coding):
    """ReasonForVisitSettingCoding."""

    class Meta:
        db_table = "canvas_sdk_data_api_reasonforvisitsettingcoding_001"

    objects: models.Manager["ReasonForVisitSettingCoding"]

    duration = ArrayField(models.DurationField())


__exports__ = ("ReasonForVisitSettingCoding",)
