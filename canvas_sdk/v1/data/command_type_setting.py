from django.db import models

from canvas_sdk.v1.data.base import Model


class CommandTypeSetting(Model):
    """Whether a command type is turned on for this instance, by its schema key."""

    class Meta:
        db_table = "canvas_sdk_data_api_commandtypesettings_001"

    schema_key = models.CharField(max_length=50)
    active = models.BooleanField()

    def __str__(self) -> str:
        return self.schema_key


__exports__ = ("CommandTypeSetting",)
