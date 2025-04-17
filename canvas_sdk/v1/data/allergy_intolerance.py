from typing import cast

from django.db import models

from canvas_sdk.v1.data.base import (
    BaseModelManager,
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
    ValueSetLookupQuerySet,
)


class AllergyIntoleranceQuerySet(
    ValueSetLookupQuerySet,
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
):
    """AllergyIntoleranceQuerySet."""

    pass


AllergyIntoleranceManager = BaseModelManager.from_queryset(AllergyIntoleranceQuerySet)


class AllergyIntolerance(models.Model):
    """AllergyIntolerance."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_allergyintolerance_001"

    objects = cast(AllergyIntoleranceQuerySet, AllergyIntoleranceManager())

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    deleted = models.BooleanField()
    committer = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, null=True)
    entered_in_error = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, null=True)
    patient = models.ForeignKey(
        "v1.Patient",
        on_delete=models.DO_NOTHING,
        related_name="allergy_intolerances",
        null=True,
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
        related_name="codings",
        null=True,
    )


__exports__ = ("AllergyIntolerance", "AllergyIntoleranceCoding")
