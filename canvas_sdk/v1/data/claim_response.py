from typing import cast

from django.db import models

from canvas_sdk.v1.data.base import CommittableModelManager, CommittableQuerySet, TimestampedModel


class ClaimResponseStatus(models.TextChoices):
    """Clearinghouse or payer verdict on a submitted claim."""

    REJECTED = "R"
    ACCEPTED = "A"


class ClaimResponse(TimestampedModel):
    """A clearinghouse or payer response to a submitted claim."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_claimresponse_001"

    objects = cast(CommittableQuerySet, CommittableModelManager())

    originator = models.ForeignKey("v1.CanvasUser", on_delete=models.PROTECT, related_name="+")
    committer = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.PROTECT, related_name="+", null=True
    )
    entered_in_error = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.PROTECT, related_name="+", null=True
    )
    deleted = models.BooleanField(default=False)

    claim = models.ForeignKey(
        "v1.Claim", on_delete=models.CASCADE, related_name="claim_responses", null=True
    )
    batch_id = models.CharField(max_length=255, blank=True, null=True)
    billing_provider_npi = models.CharField(max_length=10, blank=True, null=True)
    billing_provider_tax_id = models.CharField(max_length=100, blank=True, null=True)
    clearinghouse_claim_id = models.CharField(max_length=255, blank=True, null=True)
    from_date = models.DateField(null=True, blank=True)
    file_id = models.CharField(max_length=255, blank=True, null=True)
    file_name = models.CharField(max_length=255, blank=True, null=True)
    subscriber_number = models.CharField(max_length=100, blank=True, null=True)
    payer_id = models.CharField(max_length=255, blank=True, null=True)
    remote_claim_id = models.CharField(max_length=255, blank=True, null=True)
    response_time = models.DateTimeField(null=True, blank=True)
    sender_icn = models.CharField(max_length=255, blank=True, null=True)
    sender_name = models.CharField(max_length=255, blank=True, null=True)
    sender_id = models.CharField(max_length=255, blank=True, null=True)
    # Values come straight from the clearinghouse; ClaimResponseStatus names the two Canvas acts on.
    status = models.CharField(max_length=5, blank=True, null=True)
    total_charge = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)


class ClaimResponseDetail(TimestampedModel):
    """One message within a claim response."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_response_001"

    claim_response = models.ForeignKey(
        ClaimResponse, on_delete=models.CASCADE, related_name="responses", null=True
    )
    clearinghouse_response_id = models.CharField(max_length=255, null=True, blank=True)
    fields = models.CharField(max_length=255, blank=True, null=True)
    response_code = models.CharField(max_length=100, blank=True, null=True)
    response = models.CharField(max_length=1000, blank=True, null=True)
    status = models.CharField(max_length=5, blank=True, null=True)


__exports__ = (
    "ClaimResponse",
    "ClaimResponseStatus",
    "ClaimResponseDetail",
)
