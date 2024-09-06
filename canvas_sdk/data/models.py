from django.db import models


class CoolPatient(models.Model):
    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "dal_patient"

    id = models.CharField(max_length=32, db_column="key")
    dbid = models.BigIntegerField(db_column="id", primary_key=True)
    first_name = models.CharField()
    last_name = models.CharField()
    birth_date = models.DateField()


class Condition(models.Model):
    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "dal_api_condition"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    onset_date = models.DateField()
    resolution_date = models.DateField()
    entered_in_error_id = models.BigIntegerField()
    committer_id = models.BigIntegerField()
    patient = models.ForeignKey(
        CoolPatient, on_delete=models.DO_NOTHING, db_column="patient_id", related_name="conditions"
    )


class ConditionCoding(models.Model):
    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "dal_api_conditioncoding"

    dbid = models.BigIntegerField(primary_key=True)
    system = models.CharField()
    version = models.CharField()
    code = models.CharField()
    display = models.CharField()
    user_selected = models.BooleanField()
    condition = models.ForeignKey(
        Condition, on_delete=models.DO_NOTHING, db_column="condition_dbid", related_name="codings"
    )


class Medication(models.Model):
    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "dal_api_medication"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    patient = models.ForeignKey(
        CoolPatient, on_delete=models.DO_NOTHING, db_column="patient_id", related_name="medications"
    )
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
        db_table = "dal_api_medicationcoding"

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
