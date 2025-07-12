from typing import Self, cast

from django.db import models
from django.db.models import TextChoices

from canvas_sdk.v1.data.base import (
    BaseModelManager,
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
    IdentifiableModel,
    Model,
    ValueSetLookupQuerySet,
)


class Status(TextChoices):
    """Medication status."""

    ACTIVE = "active", "active"
    INACTIVE = "inactive", "inactive"


class MedicationQuerySet(ValueSetLookupQuerySet, CommittableQuerySetMixin, ForPatientQuerySetMixin):
    """MedicationQuerySet."""

    def active(self) -> Self:
        """Filter by active medications."""
        return self.committed().filter(status=Status.ACTIVE)


MedicationManager = BaseModelManager.from_queryset(MedicationQuerySet)


class Medication(IdentifiableModel):
    """Medication."""

    class Meta:
        db_table = "canvas_sdk_data_api_medication_001"

    objects = cast(MedicationQuerySet, MedicationManager())

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="medications", null=True
    )
    deleted = models.BooleanField()
    entered_in_error = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    committer = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    status = models.CharField(choices=Status.choices, max_length=20)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    quantity_qualifier_description = models.TextField()
    clinical_quantity_description = models.TextField()
    potency_unit_code = models.CharField(max_length=20)
    national_drug_code = models.CharField(max_length=20)
    erx_quantity = models.FloatField()


class MedicationCoding(Model):
    """MedicationCoding."""

    class Meta:
        db_table = "canvas_sdk_data_api_medicationcoding_001"

    system = models.CharField(max_length=255)
    version = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    display = models.CharField(max_length=1000)
    user_selected = models.BooleanField()
    medication = models.ForeignKey(
        Medication, on_delete=models.DO_NOTHING, related_name="codings", null=True
    )


__exports__ = ("Status", "Medication", "MedicationCoding")
