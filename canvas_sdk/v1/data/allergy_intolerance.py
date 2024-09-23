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
    # created
    # modified
    # originator_id
    # editors
    deleted = models.BooleanField()
    committer_id = models.BigIntegerField()
    entered_in_error_id = models.BigIntegerField()
    patient = models.ForeignKey(
        Patient,
        on_delete=models.DO_NOTHING,
        db_column="patient_id",
        related_name="allergy_intolerances",
    )
    # note_id
    # allergy_intolerance_type
    # category
    # status
    # severity
    onset_date = models.DateField()
    # onset_date_original_input
    last_occurence = models.DateField()
    # last_occurence_original_input
    recorded_date = models.DateTimeField()
    # narrative


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
