from typing import Self, cast

from django.db import models
from django.db.models import TextChoices

from canvas_sdk.v1.data.base import (
    BaseModelManager,
    BaseQuerySet,
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
    ValueSetLookupQuerySetMixin,
)


class ClinicalStatus(TextChoices):
    """Condition clinical status."""

    ACTIVE = "active", "active"
    RELAPSE = "relapse", "relapse"
    REMISSION = "remission", "remission"
    RESOLVED = "resolved", "resolved"
    INVESTIGATIVE = "investigative", "investigative"


class ConditionQuerySet(
    BaseQuerySet,
    ValueSetLookupQuerySetMixin,
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
):
    """ConditionQuerySet."""

    def active(self) -> Self:
        """Return a queryset that filters for active conditions."""
        return self.committed().filter(clinical_status=ClinicalStatus.ACTIVE)


ConditionManager = BaseModelManager.from_queryset(ConditionQuerySet)


class Condition(models.Model):
    """Condition."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_condition_001"

    objects = cast(ConditionQuerySet, ConditionManager())

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    deleted = models.BooleanField()
    entered_in_error = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, null=True)
    committer = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, null=True)
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="conditions", null=True
    )
    onset_date = models.DateField()
    resolution_date = models.DateField()
    clinical_status = models.CharField(choices=ClinicalStatus.choices)


class ConditionCoding(models.Model):
    """ConditionCoding."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_conditioncoding_001"

    dbid = models.BigIntegerField(primary_key=True)
    system = models.CharField()
    version = models.CharField()
    code = models.CharField()
    display = models.CharField()
    user_selected = models.BooleanField()
    condition = models.ForeignKey(
        Condition, on_delete=models.DO_NOTHING, related_name="codings", null=True
    )


__exports__ = (
    "ClinicalStatus",
    "Condition",
    "ConditionCoding",
)
