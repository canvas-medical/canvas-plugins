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
    ValueSetLookupQuerySetMixin,
)
from canvas_sdk.v1.data.coding import Coding
from canvas_sdk.v1.data.task import Task


class Referral(AuditedModel, IdentifiableModel):
    """Referral."""

    class Meta:
        db_table = "canvas_sdk_data_api_referral_001"

    patient = models.ForeignKey("v1.Patient", on_delete=models.DO_NOTHING)
    note = models.ForeignKey("v1.Note", on_delete=models.DO_NOTHING)
    service_provider = models.ForeignKey(
        "v1.ServiceProvider",
        on_delete=models.CASCADE,
        related_name="referrals",
        null=True,
        blank=True,
    )
    assessments = models.ManyToManyField("v1.Assessment", related_name="referrals", blank=True)
    clinical_question = models.CharField(max_length=50)
    priority = models.CharField(max_length=255)
    include_visit_note = models.BooleanField()
    notes = models.TextField()
    date_referred = models.DateTimeField()
    forwarded = models.BooleanField()
    internal_comment = models.TextField()
    internal_task_comment = models.OneToOneField(
        "v1.TaskComment", on_delete=models.SET_NULL, null=True, related_name="referral"
    )
    ignored = models.BooleanField()

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

    def __str__(self) -> str:
        return f"Referral {self.id}"


class ReferralReportTimeframeLookupQuerySetMixin(TimeframeLookupQuerySetMixin):
    """A class that adds queryset functionality to filter using timeframes."""

    @property
    def timeframe_filter_field(self) -> str:
        """Returns the field that should be filtered on."""
        return "original_date"


class ReferralReportQuerySet(
    BaseQuerySet,
    ForPatientQuerySetMixin,
    ReferralReportTimeframeLookupQuerySetMixin,
):
    """QuerySet for ReferralReport with value set matching via codings."""

    def find(self, value_set: type["ValueSet"]) -> Self:  # type: ignore[name-defined]
        """
        Filters referral reports to those found in the ValueSet via codings.

        For example:
        from canvas_sdk.v1.data.referral import ReferralReport
        from canvas_sdk.value_set.v2022.procedure import Colonoscopy
        colonoscopy_reports = ReferralReport.objects.find(Colonoscopy)
        """
        from canvas_sdk.value_set.value_set import ValueSet
        from django.db.models import Q

        q_filter = Q()
        for system, codes in ValueSetLookupQuerySetMixin.codings(value_set):
            q_filter |= Q(codings__system=system, codings__code__in=codes)
        return self.filter(q_filter).distinct()


class BaseReferralReportManager(models.Manager):
    """Base manager for ReferralReport that doesn't filter by deleted field."""

    def get_queryset(self):
        """Return queryset without filtering by deleted (ReferralReport uses junked instead)."""
        return ReferralReportQuerySet(self.model, using=self._db)


ReferralReportManager = BaseReferralReportManager.from_queryset(ReferralReportQuerySet)


class ReferralReport(TimestampedModel, IdentifiableModel):
    """ReferralReport."""

    class Meta:
        db_table = "canvas_sdk_data_api_referralreport_001"

    objects = cast(ReferralReportQuerySet, ReferralReportManager())

    originator = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )

    review_mode = models.CharField(max_length=2)
    assigned_by = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    junked = models.BooleanField()
    requires_signature = models.BooleanField()
    assigned_date = models.DateTimeField(null=True)
    team_assigned_date = models.DateTimeField(null=True)
    team = models.ForeignKey("v1.Team", on_delete=models.DO_NOTHING, null=True)
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="referral_reports"
    )
    referral = models.ForeignKey(
        Referral, on_delete=models.DO_NOTHING, related_name="reports", null=True
    )
    specialty = models.CharField(max_length=250)
    original_date = models.DateField(null=True)
    comment = models.TextField()
    priority = models.BooleanField(default=False)


class ReferralReportCoding(Coding):
    """ReferralReportCoding."""

    class Meta:
        db_table = "canvas_sdk_data_api_referralreportcoding_001"

    report = models.ForeignKey(
        ReferralReport, on_delete=models.DO_NOTHING, related_name="codings", null=True, db_column="report_id"
    )
    value = models.CharField(max_length=1000)


__exports__ = ("Referral", "ReferralReport", "ReferralReportCoding")