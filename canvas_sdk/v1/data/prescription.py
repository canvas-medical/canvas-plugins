from typing import Self, cast

from django.db import models
from django.utils import timezone

from canvas_sdk.v1.data.base import (
    AuditedModel,
    BaseModelManager,
    BaseQuerySet,
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
    IdentifiableModel,
)


class PrescrptionStatus(models.TextChoices):
    """Prescription Status."""

    ACTIVE = "active", "active"
    INACTIVE = "inactive", "inactive"

    OPEN = "open", "Open"
    PENDING = "pending", "Pending"
    ACCEPTED = "ultimately-accepted", "Ultimately Accepted"
    ERROR = "error", "Error"
    CANCEL_REQUESTED = "cancel-requested", "Cancel Requested"
    CANCELED = "canceled", "Canceled"
    CANCEL_DENIED = "cancel-denied", "Cancel Denied"
    RECEIVED = "received", "Received by DrFirst"
    SIGNED = "signed", "Signed"
    INQUEUE = "inqueue", "In Queue"
    TRANSMITTED = "transmitted", "Transmitted"
    DELIVERED = "delivered", "Delivered"


class PrescriptionResponse(models.TextChoices):
    """Prescription Response."""

    APPROVED = "A", "Approved"
    APPROVED_WITH_CHANGES = "C", "Approved with changes"
    DENIED = "D", "Denied"
    DENIED_PRESCRIPTION_TO_FOLLOW = "N", "Denied, new prescription to follow"


class PrescriptionQuerySet(
    BaseQuerySet,
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
):
    """PrescriptionQuerySet."""

    def active(self) -> Self:
        """Filter prescriptions."""
        return self.committed().exclude(response_type=PrescriptionResponse.DENIED)


PrescriptionManager = BaseModelManager.from_queryset(PrescriptionQuerySet)


class Prescription(IdentifiableModel, AuditedModel):
    """Prescription."""

    class Meta:
        db_table = "canvas_sdk_data_api_prescription_001"
        ordering = ["id"]

    objects = cast(PrescriptionQuerySet, PrescriptionManager())

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.CASCADE, related_name="prescriptions", null=True
    )
    note = models.ForeignKey(
        "v1.Note", on_delete=models.CASCADE, related_name="prescriptions", null=True
    )
    supervising_provider = models.ForeignKey(
        "v1.Staff",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supervising_prescriptions",
    )
    medication = models.ForeignKey(
        "v1.Medication", on_delete=models.CASCADE, related_name="prescriptions", null=True
    )
    compound_medication = models.ForeignKey(
        "v1.CompoundMedication",
        on_delete=models.CASCADE,
        related_name="compound_medication",
        null=True,
    )
    previous_medication = models.ForeignKey(
        "v1.Medication", on_delete=models.CASCADE, related_name="previous_medications", null=True
    )

    prescriber = models.ForeignKey("v1.Staff", on_delete=models.CASCADE, null=True, blank=True)
    is_refill = models.BooleanField(default=False)
    is_adjustment = models.BooleanField(default=False)
    error_message = models.TextField(default="", blank=True)
    written_date = models.DateTimeField(default=timezone.now)
    dispensed_date = models.DateTimeField(null=True, blank=True, db_index=True)
    indications = models.ManyToManyField(
        "v1.Assessment", related_name="treatments_prescribed", blank=True
    )
    note_to_pharmacist = models.CharField(max_length=1024, blank=True, default="")
    end_date = models.DateField(null=True, default=None, blank=True)
    end_date_original_input = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(
        choices=PrescrptionStatus, max_length=50, null=True, default=PrescrptionStatus.OPEN
    )
    dose_quantity = models.FloatField(null=True, blank=True)
    dose_form = models.CharField(max_length=255, blank=True, default="")
    dose_route = models.CharField(max_length=255, blank=True, default="")
    dose_frequency = models.FloatField(null=True, blank=True)
    dose_frequency_interval = models.CharField(max_length=255, blank=True, default="")
    sig_original_input = models.CharField(max_length=1000, blank=True, default="")
    maximum_daily_dose = models.CharField(max_length=255, blank=True, default="")
    dispense_quantity = models.FloatField(null=True, blank=True)
    potency_quantity = models.FloatField(null=True, blank=True)
    duration_in_days = models.IntegerField(null=True, blank=True)
    count_of_refills_allowed = models.IntegerField(null=True, blank=True)
    generic_substitutions_allowed = models.BooleanField(default=True)

    # Pharmacy details
    pharmacy_name = models.CharField(max_length=512, blank=True, default="")
    pharmacy_ncpdp_id = models.CharField(max_length=512, blank=True, default="")
    pharmacy_address = models.CharField(max_length=512, blank=True, default="")
    pharmacy_phone_number = models.CharField(max_length=50, blank=True, default="")
    pharmacy_fax_number = models.CharField(max_length=50, blank=True, default="")
    pharmacy_is_read_only = models.BooleanField(default=False)

    # From Surescripts
    message_id = models.CharField(max_length=35, blank=True, default="")
    prescription_order_number = models.CharField(max_length=35, blank=True, default="")

    # Indicates that this is a refill_response
    response_type = models.CharField(
        max_length=1, choices=PrescriptionResponse, null=True, blank=True
    )
    reason_code = models.CharField(max_length=3, null=True, blank=True)
    # TODO: uncomment when RefillRequest is added to Data Module
    # refill_request = models.ForeignKey(
    #     "v1.RefillRequest", on_delete=models.CASCADE, null=True, blank=True, related_name="response"
    # )
    related_refill = models.OneToOneField("self", on_delete=models.CASCADE, null=True, blank=True)
    is_epcs = models.BooleanField(null=True, default=False)


__exports__ = ("Prescription", "PrescriptionStatus", "PrescriptionResponse")
