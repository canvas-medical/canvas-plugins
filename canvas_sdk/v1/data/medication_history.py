from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import TextChoices

from canvas_sdk.v1.data.base import (
    IdentifiableModel,
    TimestampedModel,
)
from canvas_sdk.v1.data.coding import Coding


class MedicationHistoryMedication(TimestampedModel, IdentifiableModel):
    """MedicationHistoryMedication."""

    class Meta:
        db_table = "canvas_sdk_data_api_medicationhistorymedication_001"

    patient = models.ForeignKey(
        "v1.Patient",
        on_delete=models.DO_NOTHING,
        related_name="medication_history_medications",
        null=True,
    )

    drug_description = models.TextField(blank=True, default="")

    strength_value = models.CharField(max_length=255, blank=True, default="")
    strength_form = models.CharField(max_length=255, blank=True, default="")
    strength_unit_of_measure = models.CharField(max_length=255, blank=True, default="")

    quantity = models.FloatField(null=True)
    quantity_unit_of_measure = models.CharField(max_length=255, blank=True, default="")
    quantity_code_list_qualifier = models.CharField(max_length=255, blank=True, default="")

    days_supply = models.IntegerField(null=True)

    last_fill_date = models.DateTimeField(db_index=True)
    written_date = models.DateTimeField(blank=True, null=True)

    other_date = models.DateTimeField(blank=True, null=True)
    other_date_qualifier = models.CharField(max_length=255, blank=True, default="")

    substitutions = models.BooleanField(null=True)

    refills_remaining = models.IntegerField(null=True)

    diagnosis_code = models.CharField(max_length=255, blank=True, default="")
    diagnosis_qualifier = models.CharField(max_length=255, blank=True, default="")
    diagnosis_description = models.CharField(max_length=255, blank=True, default="")

    secondary_diagnosis_code = models.CharField(max_length=255, blank=True, default="")
    secondary_diagnosis_qualifier = models.CharField(max_length=255, blank=True, default="")
    secondary_diagnosis_description = models.CharField(max_length=255, blank=True, default="")

    dea_schedule = models.CharField(max_length=255, blank=True, default="")

    potency_unit_code = models.CharField(max_length=20, blank=True, default="")
    etc_path_id = ArrayField(base_field=models.IntegerField(), null=True)
    etc_path_name = ArrayField(base_field=models.CharField(max_length=255), null=True)

    fill_number = models.IntegerField(blank=True, null=True)

    prescriber_order_number = models.CharField(max_length=255, blank=True, default="")

    source_description = models.CharField(max_length=255, blank=True, default="")
    source_qualifier = models.CharField(max_length=255, blank=True, default="")
    source_payer_id = models.CharField(max_length=255, blank=True, default="")
    source_type = models.CharField(max_length=255, blank=True, default="")

    note = models.TextField(blank=True, default="")
    sig = models.TextField(blank=True, default="")

    prior_authorization_status = models.CharField(max_length=255, blank=True, default="")
    prior_authorization = models.CharField(max_length=255, blank=True, default="")

    pharmacy_name = models.CharField(max_length=255, blank=True, default="")
    pharmacy_ncpdp_id = models.CharField(max_length=255, blank=True, default="")
    pharmacy_npi = models.CharField(max_length=255, blank=True, default="")

    prescriber_business_name = models.CharField(max_length=255, blank=True, default="")
    prescriber_first_name = models.CharField(max_length=255, blank=True, default="")
    prescriber_last_name = models.CharField(max_length=255, blank=True, default="")
    prescriber_npi = models.CharField(max_length=255, blank=True, default="")
    prescriber_dea_number = models.CharField(max_length=255, blank=True, default="")


class MedicationHistoryMedicationCoding(Coding):
    """MedicationHistoryMedicationCoding."""

    class Meta:
        db_table = "canvas_sdk_data_api_medicationhistorymedicationcoding_001"

    medication = models.ForeignKey(
        MedicationHistoryMedication, on_delete=models.CASCADE, related_name="codings"
    )


class MedicationHistoryResponseStatus(TextChoices):
    """MedicationHistoryResponseStatus."""

    STATUS_APPROVED = "approved"
    STATUS_DENIED = "denied"


class MedicationHistoryResponse(TimestampedModel, IdentifiableModel):
    """MedicationHistoryResponse."""

    class Meta:
        db_table = "canvas_sdk_data_api_medicationhistoryresponse_001"

    patient = models.ForeignKey(
        "v1.Patient",
        on_delete=models.CASCADE,
        related_name="medication_history_responses",
    )
    staff = models.ForeignKey(
        "v1.Staff",
        on_delete=models.CASCADE,
        related_name="medication_history_responses",
        null=True,
    )

    message_id = models.CharField(max_length=35, blank=True, default="", db_index=True)
    related_to_message_id = models.CharField(max_length=35, blank=True, default="", db_index=True)

    status = models.CharField(choices=MedicationHistoryResponseStatus.choices, max_length=20)

    reason = models.TextField(blank=True, default="")
    reason_code = models.CharField(max_length=2, blank=True, default="")

    note = models.TextField(blank=True, default="")

    start_date = models.DateField()
    end_date = models.DateField()


__exports__ = (
    "MedicationHistoryMedication",
    "MedicationHistoryMedicationCoding",
    "MedicationHistoryResponseStatus",
    "MedicationHistoryResponse",
)
