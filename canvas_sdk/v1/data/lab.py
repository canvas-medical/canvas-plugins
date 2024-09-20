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
    review_mode = models.CharField(max_length=2)
    junked = models.BooleanField()
    requires_signature = models.BooleanField()
    assigned_date = models.DateTimeField(null=True)
    patient = models.ForeignKey(
        Patient, on_delete=models.DO_NOTHING, related_name="lab_reports", null=True
    )
    transmission_type = models.CharField(max_length=2)
    for_test_only = models.BooleanField()
    report_data_payload_cache = models.JSONField(blank=True, null=True)
    external_id = models.CharField(max_length=40, blank=True)
    version = models.IntegerField()
    requisition_number = models.CharField(max_length=40, blank=True)
    review = models.ForeignKey(
        "LabReview", related_name="reports", null=True, on_delete=models.DO_NOTHING
    )
    original_date = models.DateTimeField(null=True)
    date_performed = models.DateTimeField(null=True)
    custom_document_name = models.CharField(blank=True)
    originator = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING, null=True)
    committer = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING, null=True)
    entered_in_error = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING, null=True)
    deleted = models.BooleanField()


class LabReview(models.Model):
    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_labreview_001"

    objects = CommittableModelManager()

    # id = models.UUIDField() # TODO - add externally_exposable_id in home-app
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    originator = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING, null=True)
    deleted = models.BooleanField()
    committer = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING, null=True)
    entered_in_error = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING, null=True)
    internal_comment = models.TextField(blank=True)
    message_to_patient = models.CharField(max_length=2048, blank=True)
    status = models.CharField(max_length=50, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.DO_NOTHING)
    patient_communication_method = models.CharField(max_length=30)


class LabValue(models.Model):
    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_labvalue_001"

    # id = models.UUIDField() # TODO - add externally_exposable_id in home-app
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    report = models.ForeignKey(
        "LabReport", related_name="values", null=True, on_delete=models.DO_NOTHING
    )
    value = models.TextField(blank=True)
    units = models.CharField(max_length=30, blank=True)
    abnormal_flag = models.CharField(max_length=128, blank=True)
    reference_range = models.CharField(max_length=128, blank=True)
    low_threshold = models.CharField(max_length=30, blank=True)
    high_threshold = models.CharField(max_length=30, blank=True)
    comment = models.TextField(max_length=2000, blank=True)
    observation_status = models.CharField(blank=True, max_length=24)


class LabValueCoding(models.Model):
    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_labvaluecoding_001"

    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    value = models.ForeignKey(
        LabValue, on_delete=models.DO_NOTHING, related_name="codings", null=True
    )
    code = models.CharField(max_length=128, blank=True)
    name = models.CharField(max_length=256, blank=True)
    # there is no system in the database; these are all assumed to be LOINC codes
