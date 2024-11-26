from django.db import models
from django.db.models import TextChoices

from canvas_sdk.v1.data.base import ValueSetLookupQuerySet
from canvas_sdk.v1.data.patient import Patient
from canvas_sdk.v1.data.user import CanvasUser


class ClinicalStatus(TextChoices):
    """Condition clinical status."""

    ACTIVE = "active", "active"
    RELAPSE = "relapse", "relapse"
    REMISSION = "remission", "remission"
    RESOLVED = "resolved", "resolved"
    INVESTIGATIVE = "investigative", "investigative"


class ConditionQuerySet(ValueSetLookupQuerySet):
    """ConditionQuerySet."""

    pass


class Condition(models.Model):
    """Condition."""

    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_condition_001"

    objects = ConditionQuerySet.as_manager()

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    onset_date = models.DateField()
    resolution_date = models.DateField()
    clinical_status = models.CharField(choices=ClinicalStatus.choices)
    deleted = models.BooleanField()
    entered_in_error = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING)
    committer = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING)
    patient = models.ForeignKey(Patient, on_delete=models.DO_NOTHING, related_name="conditions")


class ConditionCoding(models.Model):
    """ConditionCoding."""

    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_conditioncoding_001"

    dbid = models.BigIntegerField(primary_key=True)
    system = models.CharField()
    version = models.CharField()
    code = models.CharField()
    display = models.CharField()
    user_selected = models.BooleanField()
    condition = models.ForeignKey(Condition, on_delete=models.DO_NOTHING, related_name="codings")
