from django.db import models


class AssessmentStatus(models.TextChoices):
    """AssessmentStatus."""

    STATUS_IMPROVING = "improved", "Improved"
    STATUS_STABLE = "stable", "Unchanged"
    STATUS_DETERIORATING = "deteriorated", "Deteriorated"


class Assessment(models.Model):
    """Assessment."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_assessment_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    originator = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING)
    committer = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, null=True)
    deleted = models.BooleanField()
    entered_in_error = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, null=True)
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
    status = models.CharField(choices=AssessmentStatus.choices)
    narrative = models.CharField()
    background = models.CharField()
    care_team = models.CharField()


__exports__ = ("AssessmentStatus", "Assessment")
