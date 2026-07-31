from typing import cast

from django.contrib.postgres.fields import ArrayField
from django.db import models

from canvas_sdk.v1.data.base import (
    AuditedModel,
    CommittableModelManager,
    CommittableQuerySet,
)


class EducationalMaterial(AuditedModel):
    """Model to read EducationalMaterial command data."""

    class Meta:
        db_table = "canvas_sdk_data_api_educationalmaterial_001"

    objects = cast(CommittableQuerySet, CommittableModelManager())

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="education_material"
    )
    note = models.ForeignKey(
        "v1.Note", on_delete=models.DO_NOTHING, related_name="education_material"
    )
    article_id = models.TextField(blank=True, default="")
    selected_language = models.CharField(max_length=6, default="en-us")
    title = models.TextField(blank=True, default="")
    languages = ArrayField(models.CharField(max_length=6, default=""), blank=True, default=list)
    abstract = models.TextField(blank=True, default="")


__exports__ = ("EducationalMaterial",)
