from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel


class ClaimDiagnosisCode(IdentifiableModel):
    """ClaimDiagnosisCode model for claim diagnosis codes."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_claimdiagnosiscode_001"
        ordering = ["rank"]

    claim = models.ForeignKey("v1.Claim", on_delete=models.CASCADE, related_name="diagnosis_codes")
    rank = models.IntegerField()
    code = models.CharField(max_length=20, blank=True)
    display = models.CharField(max_length=1000, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


__exports__ = ("ClaimDiagnosisCode",)
