from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel
from canvas_sdk.v1.data.coding import Coding
from canvas_sdk.v1.data.report import Report
from canvas_sdk.v1.data.utils import presigned_url


class DocumentCoding(Coding):
    """DocumentCoding."""

    class Meta:
        db_table = "canvas_sdk_data_api_documentcoding_001"


class PatientAdministrativeDocument(TimestampedModel, IdentifiableModel, Report):
    """Model to read PatientAdministrativeDocument data."""

    class Meta:
        db_table = "canvas_sdk_data_api_patientadministrativedocument_001"

    patient = models.ForeignKey("v1.Patient", on_delete=models.DO_NOTHING, related_name="+")
    originator = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    reviewers = models.ManyToManyField(
        "v1.Staff",
        related_name="+",
        db_table="canvas_sdk_data_api_patientadministrativedocument_reviewers_001",
        blank=True,
    )
    integration_task_review = models.ForeignKey(
        "v1.IntegrationTaskReview", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    code = models.ForeignKey(
        DocumentCoding, on_delete=models.DO_NOTHING, null=True, related_name="+"
    )

    name = models.CharField(max_length=255)
    original_date = models.DateField(null=True)
    comment = models.TextField(default="", blank=True)
    priority = models.BooleanField(default=False)
    document = models.FileField(max_length=255)

    @property
    def document_url(self) -> str | None:
        """Return a presigned URL for the document file, or None if unset."""
        if self.document:
            return presigned_url(self.document.name)
        return None


__exports__ = ("DocumentCoding", "PatientAdministrativeDocument")
