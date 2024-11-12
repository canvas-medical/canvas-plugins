from django.db import models

from canvas_sdk.v1.data.common import (
    DocumentReviewMode,
    OrderStatus,
    ReviewPatientCommunicationMethod,
    ReviewStatus,
)
from canvas_sdk.v1.data.patient import Patient
from canvas_sdk.v1.data.user import CanvasUser


class ImagingOrder(models.Model):
    """Model to read ImagingOrder data."""

    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_imagingorder_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    originator = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING)
    deleted = models.BooleanField()
    committer = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING)
    entered_in_error = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING)
    patient = models.ForeignKey(Patient, on_delete=models.DO_NOTHING, related_name="imaging_orders")
    # TODO - uncomment when Note model is complete
    #  note = models.ForeigneKey(Note, on_delete=models.DO_NOTHING, related_name="imaging_orders")
    imaging = models.CharField()
    # TODO - uncomment when ServiceProvider model is complete
    # imaging_center = models.ForeignKey(ServiceProvider, related_name="imaging_orders", null=True, on_delete=models.DO_NOTHING)
    note_to_radiologist = models.CharField()
    internal_comment = models.CharField()
    status = models.CharField(choices=OrderStatus)
    date_time_ordered = models.DateTimeField()
    priority = models.CharField()
    # TODO - uncomment when Staff model is complete
    # ordering_provider = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name="imaging_orders", null=True)
    delegated = models.BooleanField(default=False)


class ImagingReview(models.Model):
    """Model to read ImagingReview data."""

    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_imagingreview_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    originator = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING)
    deleted = models.BooleanField()
    committer = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING)
    entered_in_error = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING)
    patient_communication_method = models.CharField(choices=ReviewPatientCommunicationMethod)
    # TODO  - uncomment when Note model is complete
    # note = models.ForeignKey(Note, on_delete=models.DO_NOTHING, related_name="imaging_reviews")
    internal_comment = models.CharField()
    message_to_patient = models.CharField()
    is_released_to_patient = models.BooleanField()
    status = models.CharField(choices=ReviewStatus)
    patient = models.ForeignKey(
        Patient, on_delete=models.DO_NOTHING, related_name="imaging_reviews"
    )


class ImagingReport(models.Model):
    """Model to read ImagingReport data."""

    class ImagingReportSource(models.TextChoices):
        RADIOLOGY_FROM_PATIENT = "RADIOLOGY_PATIENT", "Radiology Report From Patient"
        VERBAL_FROM_PATIENT = "VERBAL_PATIENT", "Verbal Report From Patient"
        DIRECTLY_REPORT = "DIRECTLY_RADIOLOGY", "Directly Radiology Report"

    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_imagingreport_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    review_mode = models.CharField(choices=DocumentReviewMode)
    junked = models.BooleanField()
    requires_signature = models.BooleanField()
    assigned_date = models.DateTimeField()
    patient = models.ForeignKey(
        Patient, on_delete=models.DO_NOTHING, related_name="imaging_results"
    )
    order = models.ForeignKey(ImagingOrder, on_delete=models.DO_NOTHING, null=True)
    source = models.CharField(choices=ImagingReportSource)
    name = models.CharField()
    result_date = models.DateField()
    original_date = models.DateField()
    review = models.ForeignKey(ImagingReview, null=True, on_delete=models.DO_NOTHING)
