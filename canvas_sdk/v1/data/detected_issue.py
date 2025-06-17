from django.db import models


class DetectedIssue(models.Model):
    """DetectedIssue."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_detectedissue_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    identified = models.DateTimeField()
    deleted = models.BooleanField()
    originator = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, null=True)
    committer = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, null=True)
    entered_in_error = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, null=True)
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="detected_issues", null=True
    )
    code = models.CharField()
    status = models.CharField()
    severity = models.CharField()
    reference = models.CharField()
    issue_identifier = models.CharField()
    issue_identifier_system = models.CharField()
    detail = models.TextField()


class DetectedIssueEvidence(models.Model):
    """DetectedIssueEvidence."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_detectedissueevidence_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    system = models.CharField()
    version = models.CharField()
    code = models.CharField()
    display = models.CharField()
    user_selected = models.BooleanField()
    detected_issue = models.ForeignKey(
        DetectedIssue,
        on_delete=models.DO_NOTHING,
        related_name="evidence",
        null=True,
    )


__exports__ = ("DetectedIssue", "DetectedIssueEvidence")
