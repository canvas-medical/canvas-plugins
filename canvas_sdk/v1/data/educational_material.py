from typing import cast

from django.contrib.postgres.fields import ArrayField
from django.db import models

from canvas_sdk.v1.data.base import (
    AuditedModel,
    CommittableModelManager,
    CommittableQuerySet,
)

# Kept in sync with HW_SUPPORTED_LANGUAGES in home-app.
EDUCATIONAL_MATERIAL_LANGUAGES = (
    ("en-us", "English"),
    ("es-us", "Spanish"),
    ("en-ca", "English CA"),
    ("fr-ca", "French CA"),
    ("fr-fr", "French FR"),
    ("da-dk", "Danish DK"),
    ("ar-eg", "Arabic Egypt"),
    ("ar-us", "Arabic"),
    ("bn-us", "Bengali"),
    ("bs-ba", "Bosnian"),
    ("bs-us", "Bosnian"),
    ("fa-ir", "Farsi Iran"),
    ("fa-us", "Farsi"),
    ("hr-hr", "Croatian"),
    ("ht-us", "Haitian"),
    ("ko-us", "Korean"),
    ("ru-ru", "Russian"),
    ("ru-us", "Russian"),
    ("sr-us", "Serbian"),
    ("so-so", "Somalia"),
    ("so-us", "Somalia"),
    ("tl-us", "Tagalog"),
    ("vi-vn", "Vietnamese"),
    ("vi-us", "Vietnamese"),
    ("zh-cn", "Chinese"),
    ("zh-us", "Chinese"),
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
    selected_language = models.CharField(
        max_length=6, choices=EDUCATIONAL_MATERIAL_LANGUAGES, default="en-us"
    )
    title = models.TextField(blank=True, default="")
    languages = ArrayField(models.CharField(max_length=6, default=""), blank=True, default=list)
    abstract = models.TextField(blank=True, default="")


__exports__ = ("EducationalMaterial",)
