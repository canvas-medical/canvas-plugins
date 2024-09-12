from django.db import models

from canvas_sdk.v1.data.base import CommittableModelManager
from canvas_sdk.v1.data.patient import Patient


class Condition(models.Model):
    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_condition_001"

    objects = CommittableModelManager()

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    onset_date = models.DateField()
    resolution_date = models.DateField()
    deleted = models.BooleanField()
    entered_in_error_id = models.BigIntegerField()
    committer_id = models.BigIntegerField()
    patient = models.ForeignKey(
        Patient, on_delete=models.DO_NOTHING, db_column="patient_id", related_name="conditions"
    )


class ConditionCoding(models.Model):
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
    condition = models.ForeignKey(
        Condition, on_delete=models.DO_NOTHING, db_column="condition_dbid", related_name="codings"
    )
