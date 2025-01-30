from typing import cast

from django.db import models
from django.db.models import TextChoices

from canvas_sdk.v1.data.base import (
    BaseModelManager,
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
    ValueSetLookupQuerySet,
)


class Status(TextChoices):
    """Medication status."""

    ACTIVE = "active", "active"
    INACTIVE = "inactive", "inactive"


class MedicationQuerySet(ValueSetLookupQuerySet, CommittableQuerySetMixin, ForPatientQuerySetMixin):
    """MedicationQuerySet."""

    pass


MedicationManager = BaseModelManager.from_queryset(MedicationQuerySet)


class Medication(models.Model):
    """Medication."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_medication_001"

    objects = cast(MedicationQuerySet, MedicationManager())

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="medications", null=True
    )
    deleted = models.BooleanField()
    entered_in_error = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, null=True)
    committer = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, null=True)
    status = models.CharField(choices=Status.choices)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    quantity_qualifier_description = models.CharField()
    clinical_quantity_description = models.CharField()
    potency_unit_code = models.CharField()
    national_drug_code = models.CharField()
    erx_quantity = models.CharField()


class MedicationCoding(models.Model):
    """MedicationCoding."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_medicationcoding_001"

    dbid = models.BigIntegerField(primary_key=True)
    system = models.CharField()
    version = models.CharField()
    code = models.CharField()
    display = models.CharField()
    user_selected = models.BooleanField()
    medication = models.ForeignKey(
        Medication, on_delete=models.DO_NOTHING, related_name="codings", null=True
    )
