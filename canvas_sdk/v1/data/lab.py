from django.db import models

from canvas_sdk.v1.data.base import CommittableModelManager
from canvas_sdk.v1.data.patient import Patient
from canvas_sdk.v1.data.user import CanvasUser


class LabReport(models.Model):
    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_labreport_001"

    objects = CommittableModelManager()

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    review_mode = models.CharField()
    junked = models.BooleanField()
    requires_signature = models.BooleanField()
    assigned_date = models.DateTimeField()
    patient = models.ForeignKey(Patient, on_delete=models.DO_NOTHING, related_name="lab_reports")
    transmission_type = models.CharField()
    for_test_only = models.BooleanField()
    external_id = models.CharField()
    version = models.IntegerField()
    requisition_number = models.CharField()
    review = models.ForeignKey("LabReview", related_name="reports", on_delete=models.DO_NOTHING)
    original_date = models.DateTimeField()
    date_performed = models.DateTimeField()
    custom_document_name = models.CharField()
    originator = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING)
    committer = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING)
    entered_in_error = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING)
    deleted = models.BooleanField()


class LabReview(models.Model):
    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_labreview_001"

    objects = CommittableModelManager()

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    originator = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING)
    deleted = models.BooleanField()
    committer = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING)
    entered_in_error = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING)
    internal_comment = models.TextField()
    message_to_patient = models.CharField()
    status = models.CharField()
    patient = models.ForeignKey(Patient, on_delete=models.DO_NOTHING)
    patient_communication_method = models.CharField()


class LabValue(models.Model):
    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_labvalue_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    report = models.ForeignKey("LabReport", related_name="values", on_delete=models.DO_NOTHING)
    value = models.TextField()
    units = models.CharField()
    abnormal_flag = models.CharField()
    reference_range = models.CharField()
    low_threshold = models.CharField()
    high_threshold = models.CharField()
    comment = models.TextField()
    observation_status = models.CharField()


class LabValueCoding(models.Model):
    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_labvaluecoding_001"

    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    value = models.ForeignKey(LabValue, on_delete=models.DO_NOTHING, related_name="codings")
    code = models.CharField()
    name = models.CharField()
    system = models.CharField()
