import json

from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel
from canvas_sdk.v1.data.task import Task


class Referral(IdentifiableModel):
    """Referral."""

    class Meta:
        db_table = "canvas_sdk_data_api_referral_001"

    created = models.DateTimeField()
    modified = models.DateTimeField()
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


class ReferralReport(IdentifiableModel):
    """ReferralReport."""

    class Meta:
        db_table = "canvas_sdk_data_api_referralreport_001"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
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


__exports__ = ("Referral", "ReferralReport")
