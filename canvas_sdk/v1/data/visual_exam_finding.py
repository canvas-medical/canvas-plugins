from django.db import models

from canvas_sdk.v1.data.base import AuditedModel, IdentifiableModel
from canvas_sdk.v1.data.utils import presigned_url


class VisualExamFinding(AuditedModel, IdentifiableModel):
    """A visual exam finding (titled image plus narrative) captured on a note."""

    class Meta:
        db_table = "canvas_sdk_data_api_visualexamfinding_001"

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="visual_exam_findings"
    )
    note = models.ForeignKey(
        "v1.Note", on_delete=models.DO_NOTHING, related_name="visual_exam_findings"
    )
    image = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, default="", blank=True)
    narrative = models.TextField(default="", blank=True)

    @property
    def image_url(self) -> str | None:
        """Return a short-lived presigned URL for the image, or None when unset."""
        if self.image:
            return presigned_url(self.image)
        return None


__exports__ = ("VisualExamFinding",)
