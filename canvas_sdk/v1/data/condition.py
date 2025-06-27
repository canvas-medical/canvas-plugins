from typing import Self, cast

from django.db import models
from django.db.models import TextChoices

from canvas_sdk.v1.data.base import (
    BaseModelManager,
    BaseQuerySet,
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
    IdentifiableModel,
    Model,
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


class Condition(IdentifiableModel):
    """Condition."""

    class Meta:
        db_table = "canvas_sdk_data_api_condition_001"

    objects = cast(ConditionQuerySet, ConditionManager())

    deleted = models.BooleanField()
    entered_in_error = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    committer = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="conditions", null=True
    )
    onset_date = models.DateField()
    resolution_date = models.DateField()
    clinical_status = models.CharField(choices=ClinicalStatus.choices, max_length=20)
    surgical = models.BooleanField()


class ConditionCoding(Model):
    """ConditionCoding."""

    class Meta:
        db_table = "canvas_sdk_data_api_conditioncoding_001"

    system = models.CharField(max_length=255)
    version = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    display = models.CharField(max_length=1000)
    user_selected = models.BooleanField()
    condition = models.ForeignKey(
        Condition, on_delete=models.DO_NOTHING, related_name="codings", null=True
    )


__exports__ = (
    "ClinicalStatus",
    "Condition",
    "ConditionCoding",
)
