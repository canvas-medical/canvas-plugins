import json

from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel
from canvas_sdk.v1.data.common import (
    DocumentReviewMode,
    OrderStatus,
    ReviewPatientCommunicationMethod,
    ReviewStatus,
)
from canvas_sdk.v1.data.task import Task


class ImagingOrder(IdentifiableModel):
    """Model to read ImagingOrder data."""

    class Meta:
        db_table = "canvas_sdk_data_api_imagingorder_001"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    originator = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    deleted = models.BooleanField()
    committer = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    entered_in_error = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, related_name="+"
    )
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="imaging_orders", null=True
    )
    note = models.ForeignKey(
        "v1.Note", on_delete=models.DO_NOTHING, related_name="imaging_orders", null=True
    )
    imaging = models.CharField(max_length=1024)
    imaging_center = models.ForeignKey(
        "v1.ServiceProvider", on_delete=models.DO_NOTHING, related_name="imaging_orders", null=True
    )
    note_to_radiologist = models.CharField(max_length=1024)
    internal_comment = models.CharField(max_length=1024)
    status = models.CharField(choices=OrderStatus.choices, max_length=30)
    date_time_ordered = models.DateTimeField()
    priority = models.CharField(max_length=255)
    ordering_provider = models.ForeignKey(
        "v1.Staff", on_delete=models.DO_NOTHING, related_name="imaging_orders", null=True
    )
    delegated = models.BooleanField(default=False)

    task_ids = models.CharField(max_length=1024)

    def get_task_objects(self) -> "models.QuerySet[Task]":
        """Convert task IDs to Task objects."""
        if self.task_ids:
            task_ids = (
                json.loads(self.task_ids) if isinstance(self.task_ids, str) else self.task_ids
            )
            return Task.objects.filter(id__in=task_ids)
        return Task.objects.none()

    @property
    def task_list(self) -> list[Task]:
        """Convenience property to get task objects."""
        return list(self.get_task_objects())


class ImagingReview(IdentifiableModel):
    """Model to read ImagingReview data."""

    class Meta:
        db_table = "canvas_sdk_data_api_imagingreview_001"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    originator = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    deleted = models.BooleanField()
    committer = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    entered_in_error = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    patient_communication_method = models.CharField(
        choices=ReviewPatientCommunicationMethod.choices, max_length=30
    )
    # TODO  - uncomment when Note model is complete
    # note = models.ForeignKey('v1.Note', on_delete=models.DO_NOTHING, related_name="imaging_reviews", null=True)
    internal_comment = models.CharField(max_length=2048)
    message_to_patient = models.CharField(max_length=2048)
    is_released_to_patient = models.BooleanField()
    status = models.CharField(choices=ReviewStatus.choices, max_length=50)
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="imaging_reviews", null=True
    )


class ImagingReport(IdentifiableModel):
    """Model to read ImagingReport data."""

    class ImagingReportSource(models.TextChoices):
        RADIOLOGY_FROM_PATIENT = "RADIOLOGY_PATIENT", "Radiology Report From Patient"
        VERBAL_FROM_PATIENT = "VERBAL_PATIENT", "Verbal Report From Patient"
        DIRECTLY_REPORT = "DIRECTLY_RADIOLOGY", "Directly Radiology Report"

    class Meta:
        db_table = "canvas_sdk_data_api_imagingreport_001"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    review_mode = models.CharField(choices=DocumentReviewMode.choices, max_length=2)
    junked = models.BooleanField()
    requires_signature = models.BooleanField()
    assigned_date = models.DateTimeField()
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="imaging_results", null=True
    )
    order = models.ForeignKey(
        ImagingOrder,
        on_delete=models.DO_NOTHING,
        related_name="results",
        default=None,
        blank=True,
        null=True,
    )
    source = models.CharField(choices=ImagingReportSource.choices, max_length=18)
    name = models.CharField(max_length=255)
    result_date = models.DateField()
    original_date = models.DateField()
    review = models.ForeignKey(ImagingReview, on_delete=models.DO_NOTHING, null=True)


__exports__ = (
    "ImagingOrder",
    "ImagingReview",
    "ImagingReport",
)
