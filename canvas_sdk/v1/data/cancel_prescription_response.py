from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel


class CancelPrescriptionResponse(TimestampedModel, IdentifiableModel):
    """A response to a CancelPrescription request."""

    class Meta:
        db_table = "canvas_sdk_data_api_cancelprescriptionresponse_001"

    patient = models.ForeignKey(
        "v1.Patient",
        on_delete=models.DO_NOTHING,
        related_name="cancel_prescription_responses",
        null=True,
    )
    request = models.OneToOneField(
        "v1.CancelPrescription",
        on_delete=models.DO_NOTHING,
        related_name="response",
        null=True,
    )
    message_id = models.CharField(max_length=35)
    note = models.CharField(max_length=1024, blank=True, default="")
    reason_code = models.CharField(max_length=150, blank=True, default="")
    response = models.CharField(max_length=25, blank=True, default="")


__exports__ = ("CancelPrescriptionResponse",)
