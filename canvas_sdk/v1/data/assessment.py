from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel


class AssessmentStatus(models.TextChoices):
    """AssessmentStatus."""

    STATUS_IMPROVING = "improved", "Improved"
    STATUS_STABLE = "stable", "Unchanged"
    STATUS_DETERIORATING = "deteriorated", "Deteriorated"


class Assessment(IdentifiableModel):
    """Assessment."""

    class Meta:
        db_table = "canvas_sdk_data_api_assessment_001"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    originator = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, related_name="+")
    committer = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    deleted = models.BooleanField()
    entered_in_error = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    patient = models.ForeignKey(
        "v1.Patient",
        on_delete=models.DO_NOTHING,
        related_name="assessments",
    )
    note = models.ForeignKey("v1.Note", on_delete=models.DO_NOTHING, related_name="assessments")
    condition = models.ForeignKey(
        "v1.Condition", on_delete=models.CASCADE, related_name="assessments", null=True
    )
    interview = models.ForeignKey("v1.Interview", on_delete=models.DO_NOTHING, null=True)
    status = models.CharField(choices=AssessmentStatus.choices, max_length=20)
    narrative = models.CharField(max_length=2048)
    background = models.CharField(max_length=2048)
    care_team = models.CharField(max_length=500)


__exports__ = ("AssessmentStatus", "Assessment")
