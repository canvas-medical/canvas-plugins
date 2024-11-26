from django.db import models
from django.db.models import TextChoices

from canvas_sdk.v1.data.base import CommittableModelManager, ValueSetLookupQuerySet
from canvas_sdk.v1.data.patient import Patient
from canvas_sdk.v1.data.user import CanvasUser


class Status(TextChoices):
    """Medication status."""

    ACTIVE = "active", "active"
    INACTIVE = "inactive", "inactive"


class MedicationQuerySet(ValueSetLookupQuerySet):
    """MedicationQuerySet."""

    pass


class Medication(models.Model):
    """Medication."""

    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_medication_001"

    objects = CommittableModelManager.from_queryset(MedicationQuerySet)()

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.DO_NOTHING, related_name="medications")
    deleted = models.BooleanField()
    entered_in_error = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING)
    committer = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING)
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
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_medicationcoding_001"

    dbid = models.BigIntegerField(primary_key=True)
    system = models.CharField()
    version = models.CharField()
    code = models.CharField()
    display = models.CharField()
    user_selected = models.BooleanField()
    medication = models.ForeignKey(Medication, on_delete=models.DO_NOTHING, related_name="codings")
