from django.contrib.postgres.fields import ArrayField
from django.db import models

from canvas_sdk.v1.data.base import TimestampedModel


class LetterTemplateType(models.TextChoices):
    """Where a LetterTemplate can be used."""

    INTERVENTION = "intervention", "Intervention"
    LETTER = "letter", "Letter"
    MESSAGE = "message", "Message"


class LetterTemplate(TimestampedModel):
    """A reusable letter template."""

    class Meta:
        db_table = "canvas_sdk_data_api_lettertemplate_001"

    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    restrict_editing = models.BooleanField(default=False)
    template_type = ArrayField(
        models.CharField(max_length=64, choices=LetterTemplateType.choices),
        blank=True,
        default=list,
    )
    locations = ArrayField(models.CharField(max_length=10), blank=True, default=list)


__exports__ = ("LetterTemplate", "LetterTemplateType")
