from django.contrib.postgres.fields import ArrayField
from django.db import models

from canvas_sdk.v1.data.base import CommittableModelManager
from canvas_sdk.v1.data.patient import Patient


class AllergyIntolerance(models.Model):
    """AllergyIntolerance."""

    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_allergyintolerance_001"

    objects = CommittableModelManager()

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    originator_id = models.BigIntegerField()
    editors = ArrayField(models.IntegerField())
    deleted = models.BooleanField()
    committer_id = models.BigIntegerField()
    entered_in_error_id = models.BigIntegerField()
    patient = models.ForeignKey(
        Patient,
        on_delete=models.DO_NOTHING,
        db_column="patient_id",
        related_name="allergy_intolerances",
    )
    note_id = models.BigIntegerField()
    allergy_intolerance_type = models.CharField()
    category = models.IntegerField()
    status = models.CharField()
    severity = models.CharField()
    onset_date = models.DateField()
    onset_date_original_input = models.CharField()
    last_occurrence = models.DateField()
    last_occurrence_original_input = models.CharField()
    recorded_date = models.DateTimeField()
    narrative = models.CharField()


class AllergyIntoleranceCoding(models.Model):
    """AllergyIntoleranceCoding."""

    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_allergyintolerancecoding_001"

    dbid = models.BigIntegerField(primary_key=True)
    system = models.CharField()
    version = models.CharField()
    code = models.CharField()
    display = models.CharField()
    user_selected = models.BooleanField()
    allergy_intolerance = models.ForeignKey(
        AllergyIntolerance,
        on_delete=models.DO_NOTHING,
        db_column="allergy_intolerance_dbid",
        related_name="codings",
    )