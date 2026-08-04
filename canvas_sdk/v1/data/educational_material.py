from typing import cast

from django.contrib.postgres.fields import ArrayField
from django.db import models

from canvas_sdk.v1.data.base import (
    AuditedModel,
    CommittableModelManager,
    CommittableQuerySet,
    IdentifiableModel,
)


# Kept in sync with HW_SUPPORTED_LANGUAGES in home-app.
class EducationalMaterialLanguage(models.TextChoices):
    """Supported languages for educational material."""

    EN_US = "en-us", "English"
    ES_US = "es-us", "Spanish"
    EN_CA = "en-ca", "English CA"
    FR_CA = "fr-ca", "French CA"
    FR_FR = "fr-fr", "French FR"
    DA_DK = "da-dk", "Danish DK"
    AR_EG = "ar-eg", "Arabic Egypt"
    AR_US = "ar-us", "Arabic"
    BN_US = "bn-us", "Bengali"
    BS_BA = "bs-ba", "Bosnian"
    BS_US = "bs-us", "Bosnian"
    FA_IR = "fa-ir", "Farsi Iran"
    FA_US = "fa-us", "Farsi"
    HR_HR = "hr-hr", "Croatian"
    HT_US = "ht-us", "Haitian"
    KO_US = "ko-us", "Korean"
    RU_RU = "ru-ru", "Russian"
    RU_US = "ru-us", "Russian"
    SR_US = "sr-us", "Serbian"
    SO_SO = "so-so", "Somalia"
    SO_US = "so-us", "Somalia"
    TL_US = "tl-us", "Tagalog"
    VI_VN = "vi-vn", "Vietnamese"
    VI_US = "vi-us", "Vietnamese"
    ZH_CN = "zh-cn", "Chinese"
    ZH_US = "zh-us", "Chinese"


class EducationalMaterial(AuditedModel, IdentifiableModel):
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
        max_length=6,
        choices=EducationalMaterialLanguage.choices,
        default=EducationalMaterialLanguage.EN_US,
    )
    title = models.TextField(blank=True, default="")
    languages = ArrayField(models.CharField(max_length=6, default=""), blank=True, default=list)
    abstract = models.TextField(blank=True, default="")


__exports__ = ("EducationalMaterial",)
