from django.db import models

from canvas_sdk.v1.data.base import CommittableModelManager, ValueSetLookupQuerySet
from canvas_sdk.v1.data.patient import Patient
from canvas_sdk.v1.data.user import CanvasUser


class ConditionQuerySet(ValueSetLookupQuerySet):
    """ConditionQuerySet."""

    pass


class Condition(models.Model):
    """Condition."""

    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_condition_001"

    objects = CommittableModelManager.from_queryset(ConditionQuerySet)()

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    onset_date = models.DateField()
    resolution_date = models.DateField()
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
