from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel


class LetterTemplate(TimestampedModel, IdentifiableModel):
    """A reusable Letter template (body + subject + merge variables)."""

    class Meta:
        db_table = "canvas_sdk_data_api_lettertemplate_001"

    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=512, blank=True, default="")
    body = models.TextField(blank=True, default="")
    note_type_code = models.CharField(max_length=64, blank=True, default="")
    active = models.BooleanField(default=True)


__exports__ = ("LetterTemplate",)
