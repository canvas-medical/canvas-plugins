import json
from typing import Self, cast

from django.db import models

from canvas_sdk.v1.data.base import (
    AuditedModel,
    BaseModelManager,
    BaseQuerySet,
    ForPatientQuerySetMixin,
    IdentifiableModel,
    TimeframeLookupQuerySetMixin,
    TimestampedModel,
    ValueSetLookupQuerySet,
    ValueSetLookupQuerySetMixin,
)
from canvas_sdk.v1.data.coding import Coding
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


class ImagingReportTimeframeLookupQuerySetMixin(TimeframeLookupQuerySetMixin):
    """A class that adds queryset functionality to filter using timeframes."""

    @property
    def timeframe_filter_field(self) -> str:
        """Returns the field that should be filtered on."""
        return "original_date"


class ImagingReportQuerySet(
    BaseQuerySet,
    ForPatientQuerySetMixin,
    ImagingReportTimeframeLookupQuerySetMixin,
):
    """QuerySet for ImagingReport with value set matching via codings."""

    def find(self, value_set: type["ValueSet"]) -> Self:  # type: ignore[name-defined]
        """
        Filters imaging reports to those found in the ValueSet via codings.

        For example:
        from canvas_sdk.v1.data.imaging import ImagingReport
        from canvas_sdk.value_set.v2022.procedure import Colonoscopy
        colonoscopy_reports = ImagingReport.objects.find(Colonoscopy)
        """
        from canvas_sdk.value_set.value_set import ValueSet
        from django.db.models import Q

        q_filter = Q()
        for system, codes in ValueSetLookupQuerySetMixin.codings(value_set):
            q_filter |= Q(codings__system=system, codings__code__in=codes)
        return self.filter(q_filter).distinct()


class BaseImagingReportManager(models.Manager):
    """Base manager for ImagingReport that doesn't filter by deleted field."""
    
    def get_queryset(self):
        """Return queryset without filtering by deleted (ImagingReport uses junked instead)."""
        return ImagingReportQuerySet(self.model, using=self._db)


ImagingReportManager = BaseImagingReportManager.from_queryset(ImagingReportQuerySet)


class ImagingReport(TimestampedModel, IdentifiableModel):
    """Model to read ImagingReport data."""

    class ImagingReportSource(models.TextChoices):
        RADIOLOGY_FROM_PATIENT = "RADIOLOGY_PATIENT", "Radiology Report From Patient"
        VERBAL_FROM_PATIENT = "VERBAL_PATIENT", "Verbal Report From Patient"
        DIRECTLY_REPORT = "DIRECTLY_RADIOLOGY", "Directly Radiology Report"

    class Meta:
        db_table = "canvas_sdk_data_api_imagingreport_001"

    objects = cast(ImagingReportQuerySet, ImagingReportManager())

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


class ImagingReportCoding(Coding):
    """A class representing an imaging report coding."""

    class Meta:
        db_table = "canvas_sdk_data_api_imagingreportcoding_001"

    report = models.ForeignKey(
        ImagingReport, on_delete=models.DO_NOTHING, related_name="codings", null=True, db_column="report_id"
    )
    value = models.TextField(blank=True, default="")


__exports__ = (
    "ImagingOrder",
    "ImagingReview",
    "ImagingReport",
    "ImagingReportCoding",
)
