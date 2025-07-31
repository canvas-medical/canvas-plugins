from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel


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

    def __str__(self) -> str:
        return f"Referral {self.id}"


__exports__ = ("Referral",)
