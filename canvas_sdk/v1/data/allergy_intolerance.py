from typing import cast

from django.db import models

from canvas_sdk.v1.data.base import (
    BaseModelManager,
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
    IdentifiableModel,
    Model,
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


class AllergyIntolerance(IdentifiableModel):
    """AllergyIntolerance."""

    class Meta:
        db_table = "canvas_sdk_data_api_allergyintolerance_001"

    objects = cast(AllergyIntoleranceQuerySet, AllergyIntoleranceManager())

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField()
    committer = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    entered_in_error = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    patient = models.ForeignKey(
        "v1.Patient",
        on_delete=models.DO_NOTHING,
        related_name="allergy_intolerances",
        null=True,
    )
    note_id = models.BigIntegerField()
    allergy_intolerance_type = models.CharField(max_length=1)
    category = models.IntegerField()
    status = models.CharField(max_length=20)
    severity = models.CharField(max_length=20)
    onset_date = models.DateField()
    onset_date_original_input = models.CharField(max_length=255)
    last_occurrence = models.DateField()
    last_occurrence_original_input = models.CharField(max_length=255)
    recorded_date = models.DateTimeField()
    narrative = models.CharField(max_length=512)


class AllergyIntoleranceCoding(Model):
    """AllergyIntoleranceCoding."""

    class Meta:
        db_table = "canvas_sdk_data_api_allergyintolerancecoding_001"

    system = models.CharField(max_length=255)
    version = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    display = models.CharField(max_length=1000)
    user_selected = models.BooleanField()
    allergy_intolerance = models.ForeignKey(
        AllergyIntolerance,
        on_delete=models.DO_NOTHING,
        related_name="codings",
        null=True,
    )


__exports__ = ("AllergyIntolerance", "AllergyIntoleranceCoding")
