from typing import cast

from django.db import models

from canvas_sdk.v1.data.base import (
    AuditedModel,
    CommittableModelManager,
    CommittableQuerySet,
    IdentifiableModel,
    TimestampedModel,
)


class PrescriptionChangeResponseType(models.TextChoices):
    """Whether a Surescripts change request was approved or denied."""

    APPROVED = "A", "Approved"
    DENIED = "D", "Denied"


class PrescriptionChangeResponseStatus(models.TextChoices):
    """Status of a PrescriptionChangeResponse."""

    OPEN = "open", "Open"
    PENDING = "pending", "Pending"
    ULTIMATELY_ACCEPTED = "ultimately-accepted", "Ultimately Accepted"
    ERROR = "error", "Error"


class PrescriptionChangeRequest(TimestampedModel):
    """A Surescripts prescription change request received from a pharmacy."""

    class Meta:
        db_table = "canvas_sdk_data_api_prescriptionchangerequest_001"

    patient = models.ForeignKey(
        "v1.Patient",
        on_delete=models.DO_NOTHING,
        related_name="prescription_change_requests",
        null=True,
    )
    note = models.ForeignKey(
        "v1.Note",
        on_delete=models.DO_NOTHING,
        related_name="prescription_change_requests",
        null=True,
    )
    staff = models.ForeignKey(
        "v1.Staff",
        on_delete=models.DO_NOTHING,
        related_name="prescription_change_requests",
        null=True,
    )
    original_prescription = models.ForeignKey(
        "v1.Prescription",
        on_delete=models.DO_NOTHING,
        related_name="change_requests",
        null=True,
    )
    message_id = models.CharField(max_length=35)
    type_code = models.CharField(max_length=2, blank=True, default="")
    sub_type_code = models.CharField(max_length=1, blank=True, default="")
    content = models.JSONField(default=dict)


class PrescriptionChangeResponse(AuditedModel, IdentifiableModel):
    """A response to a Surescripts prescription change request — the anchor for the ApproveChange and DenyChange commands."""

    class Meta:
        db_table = "canvas_sdk_data_api_prescriptionchangeresponse_001"

    objects = cast(CommittableQuerySet, CommittableModelManager())

    patient = models.ForeignKey(
        "v1.Patient",
        on_delete=models.DO_NOTHING,
        related_name="prescription_change_responses",
        null=True,
    )
    note = models.ForeignKey(
        "v1.Note",
        on_delete=models.DO_NOTHING,
        related_name="prescription_change_responses",
        null=True,
    )
    medication = models.ForeignKey(
        "v1.Medication",
        on_delete=models.DO_NOTHING,
        related_name="prescription_change_responses",
        null=True,
    )
    denied_medication = models.CharField(max_length=50, blank=True, default="")
    refills = models.IntegerField(null=True, blank=True)
    note_to_pharmacist = models.CharField(max_length=1024, blank=True, default="")
    approved_drug_index = models.IntegerField(null=True, blank=True)
    reason_code = models.CharField(max_length=3, blank=True, default="")
    response_type = models.CharField(
        choices=PrescriptionChangeResponseType.choices, max_length=1, blank=True, default=""
    )
    message_id = models.CharField(max_length=35, blank=True, default="")
    status = models.CharField(
        choices=PrescriptionChangeResponseStatus.choices,
        max_length=50,
        blank=True,
        default=PrescriptionChangeResponseStatus.OPEN,
    )
    prior_authorization_number = models.CharField(max_length=50, blank=True, default="")
    request = models.ForeignKey(
        PrescriptionChangeRequest,
        on_delete=models.DO_NOTHING,
        related_name="response",
    )


__exports__ = (
    "PrescriptionChangeRequest",
    "PrescriptionChangeResponse",
    "PrescriptionChangeResponseStatus",
    "PrescriptionChangeResponseType",
)
