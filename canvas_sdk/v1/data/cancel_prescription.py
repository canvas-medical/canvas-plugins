from typing import cast

from django.db import models

from canvas_sdk.v1.data.base import (
    AuditedModel,
    CommittableModelManager,
    CommittableQuerySet,
    IdentifiableModel,
)


class CancelPrescriptionStatus(models.TextChoices):
    """Status of a CancelPrescription."""

    OPEN = "open", "Open"
    PENDING = "pending", "Pending"
    ULTIMATELY_ACCEPTED = "ultimately-accepted", "Ultimately Accepted"


class CancelPrescription(AuditedModel, IdentifiableModel):
    """A Cancel Prescription — the anchor for the CancelPrescription command."""

    class Meta:
        db_table = "canvas_sdk_data_api_cancelprescription_001"

    objects = cast(CommittableQuerySet, CommittableModelManager())

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="cancel_prescriptions"
    )
    note = models.ForeignKey(
        "v1.Note", on_delete=models.DO_NOTHING, related_name="cancel_prescriptions"
    )
    prescription = models.ForeignKey(
        "v1.Prescription",
        on_delete=models.DO_NOTHING,
        related_name="cancel_prescriptions",
        null=True,
    )
    message_id = models.CharField(max_length=35, blank=True, default="")
    status = models.CharField(
        choices=CancelPrescriptionStatus.choices,
        max_length=50,
        blank=True,
        default=CancelPrescriptionStatus.OPEN,
    )


__exports__ = ("CancelPrescription", "CancelPrescriptionStatus")
