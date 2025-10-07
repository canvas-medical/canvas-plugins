from django.db import models

from canvas_sdk.v1.data.base import AuditedModel, IdentifiableModel
from canvas_sdk.v1.data.coding import Coding


class DetectedIssue(AuditedModel, IdentifiableModel):
    """DetectedIssue."""

    class Meta:
        db_table = "canvas_sdk_data_api_detectedissue_001"

    identified = models.DateTimeField()
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


class DetectedIssueEvidence(IdentifiableModel, Coding):
    """DetectedIssueEvidence."""

    class Meta:
        db_table = "canvas_sdk_data_api_detectedissueevidence_001"

    detected_issue = models.ForeignKey(
        DetectedIssue,
        on_delete=models.DO_NOTHING,
        related_name="evidence",
        null=True,
    )


__exports__ = ("DetectedIssue", "DetectedIssueEvidence")
