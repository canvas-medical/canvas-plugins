from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel


class DetectedIssue(IdentifiableModel):
    """DetectedIssue."""

    class Meta:
        db_table = "canvas_sdk_data_api_detectedissue_001"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    identified = models.DateTimeField()
    deleted = models.BooleanField()
    originator = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    committer = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    entered_in_error = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="detected_issues", null=True
    )
    code = models.CharField(max_length=20)
    status = models.CharField(max_length=16)
    severity = models.CharField(max_length=10)
    reference = models.CharField(max_length=200)
    issue_identifier = models.CharField(max_length=255)
    issue_identifier_system = models.CharField(max_length=255)
    detail = models.TextField()


class DetectedIssueEvidence(IdentifiableModel):
    """DetectedIssueEvidence."""

    class Meta:
        db_table = "canvas_sdk_data_api_detectedissueevidence_001"

    system = models.CharField(max_length=255)
    version = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    display = models.CharField(max_length=1000)
    user_selected = models.BooleanField()
    detected_issue = models.ForeignKey(
        DetectedIssue,
        on_delete=models.DO_NOTHING,
        related_name="evidence",
        null=True,
    )


__exports__ = ("DetectedIssue", "DetectedIssueEvidence")
