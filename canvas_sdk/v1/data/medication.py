from django.db import models

from canvas_sdk.v1.data.base import CommittableModelManager
from canvas_sdk.v1.data.patient import Patient


class Medication(models.Model):
    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_medication_001"

    objects = CommittableModelManager()

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    patient = models.ForeignKey(
        Patient, on_delete=models.DO_NOTHING, db_column="patient_id", related_name="medications"
    )
    deleted = models.BooleanField()
    entered_in_error_id = models.BigIntegerField()
    committer_id = models.BigIntegerField()
    status = models.CharField()
    start_date = models.DateField()
    end_date = models.DateField()
    quantity_qualifier_description = models.CharField()
    clinical_quantity_description = models.CharField()
    potency_unit_code = models.CharField()
    national_drug_code = models.CharField()
    erx_quantity = models.CharField()


class MedicationCoding(models.Model):
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
    medication = models.ForeignKey(
        "Medication",
        on_delete=models.DO_NOTHING,
        db_column="medication_dbid",
        to_field="dbid",
        related_name="codings",
        related_query_name="codings",
    )
