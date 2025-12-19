import json
from typing import Self, cast

from django.db import models

from canvas_sdk.v1.data.base import (
    AuditedModel,
    BaseQuerySet,
    IdentifiableModel,
    Model,
    TimestampedModel,
)
from canvas_sdk.v1.data.common import (
    DocumentReviewMode,
    OrderStatus,
    ReviewPatientCommunicationMethod,
    ReviewStatus,
)
from canvas_sdk.v1.data.task import Task


class ImagingOrder(AuditedModel, IdentifiableModel):
    """Model to read ImagingOrder data."""

    class Meta:
        db_table = "canvas_sdk_data_api_imagingorder_001"

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


class ImagingReview(AuditedModel, IdentifiableModel):
    """Model to read ImagingReview data."""

    class Meta:
        db_table = "canvas_sdk_data_api_imagingreview_001"

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


class ImagingReport(TimestampedModel, IdentifiableModel):
    """Model to read ImagingReport data."""

    class ImagingReportSource(models.TextChoices):
        RADIOLOGY_FROM_PATIENT = "RADIOLOGY_PATIENT", "Radiology Report From Patient"
        VERBAL_FROM_PATIENT = "VERBAL_PATIENT", "Verbal Report From Patient"
        DIRECTLY_REPORT = "DIRECTLY_RADIOLOGY", "Directly Radiology Report"

    class Meta:
        db_table = "canvas_sdk_data_api_imagingreport_001"

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


class ImagingReportTemplateQuerySet(BaseQuerySet):
    """QuerySet for ImagingReportTemplate with filtering methods."""

    def active(self) -> Self:
        """Filter to active templates only."""
        return self.filter(active=True)

    def search(self, query: str) -> Self:
        """Search templates by keywords."""
        return self.filter(search_keywords__icontains=query)

    def custom(self) -> Self:
        """Filter to custom (user-created) templates."""
        return self.filter(custom=True)

    def builtin(self) -> Self:
        """Filter to built-in templates."""
        return self.filter(custom=False)


ImagingReportTemplateManager = models.Manager.from_queryset(ImagingReportTemplateQuerySet)


class ImagingReportTemplate(Model):
    """Model to read ImagingReportTemplate data for LLM-powered imaging report parsing."""

    class Meta:
        db_table = "canvas_sdk_data_data_integration_imagingreporttemplate_001"

    objects = cast(ImagingReportTemplateQuerySet, ImagingReportTemplateManager())

    name = models.CharField(max_length=250)
    long_name = models.CharField(max_length=1000)
    code = models.CharField(max_length=50, blank=True, default="")
    code_system = models.CharField(max_length=50, blank=True, default="")
    search_keywords = models.CharField(max_length=500, blank=True, default="")
    active = models.BooleanField(default=True)
    custom = models.BooleanField(default=True)
    rank = models.IntegerField(default=0)


class ImagingReportTemplateField(Model):
    """Model to read ImagingReportTemplateField data."""

    class Meta:
        db_table = "canvas_sdk_data_data_integration_imagingreporttemplatefield_001"

    report_template = models.ForeignKey(
        ImagingReportTemplate, on_delete=models.DO_NOTHING, related_name="fields"
    )
    sequence = models.IntegerField(default=1)
    code = models.CharField(max_length=50, blank=True, null=True)
    code_system = models.CharField(max_length=50, blank=True, default="")
    label = models.CharField(max_length=250)
    units = models.CharField(max_length=50, blank=True, null=True)
    type = models.CharField(max_length=250)
    required = models.BooleanField(default=False)


class ImagingReportTemplateFieldOption(Model):
    """Model to read ImagingReportTemplateFieldOption data."""

    class Meta:
        db_table = "canvas_sdk_data_data_integration_imagingreporttmplfieldopt_001"

    field = models.ForeignKey(
        ImagingReportTemplateField, on_delete=models.DO_NOTHING, related_name="options"
    )
    label = models.CharField(max_length=250)
    key = models.CharField(max_length=250)


__exports__ = (
    "ImagingOrder",
    "ImagingReview",
    "ImagingReport",
    "ImagingReportTemplate",
    "ImagingReportTemplateQuerySet",
    "ImagingReportTemplateField",
    "ImagingReportTemplateFieldOption",
)
