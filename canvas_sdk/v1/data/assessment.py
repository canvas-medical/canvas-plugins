from django.db import models


class AssessmentStatus(models.TextChoices):
    STATUS_IMPROVING = "improved", "Improved"
    STATUS_STABLE = "stable", "Unchanged"
    STATUS_DETERIORATING = "deteriorated", "Deteriorated"


class Assessment(models.Model):
    """Assessment."""

    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_assessment_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    originator = models.ForeignKey("CanvasUser", on_delete=models.DO_NOTHING)
    committer = models.ForeignKey("CanvasUser", on_delete=models.DO_NOTHING, null=True)
    deleted = models.BooleanField()
    entered_in_error = models.ForeignKey("CanvasUser", on_delete=models.DO_NOTHING, null=True)
    patient = models.ForeignKey(
        "Patient",
        on_delete=models.DO_NOTHING,
        related_name="assessments",
    )
    note = models.ForeignKey("Note", on_delete=models.DO_NOTHING, related_name="assessments")
    condition = models.ForeignKey(
        "Condition", on_delete=models.CASCADE, related_name="assessments", null=True
    )
    interview = models.ForeignKey("Interview", on_delete=models.DO_NOTHING, null=True)
    status = models.CharField(choices=AssessmentStatus.choices)
    narrative = models.CharField()
    background = models.CharField()
    care_team = models.CharField()
