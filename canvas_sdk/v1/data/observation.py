from typing import cast

from django.db import models

from canvas_sdk.v1.data.base import (
    BaseModelManager,
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
    ValueSetLookupQuerySet,
)


class ObservationQuerySet(
    ValueSetLookupQuerySet, CommittableQuerySetMixin, ForPatientQuerySetMixin
):
    """ObservationQuerySet."""

    pass


ObservationManager = BaseModelManager.from_queryset(ObservationQuerySet)


class Observation(models.Model):
    """Observation."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_observation_001"

    objects = cast(ObservationQuerySet, ObservationManager())

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    originator = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, null=True)
    committer = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, null=True)
    entered_in_error = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, null=True)
    deleted = models.BooleanField()
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="observations", null=True
    )
    is_member_of = models.ForeignKey(
        "self", on_delete=models.DO_NOTHING, related_name="members", null=True
    )
    category = models.CharField()
    units = models.TextField()
    value = models.TextField()
    note_id = models.BigIntegerField()
    name = models.TextField()
    effective_datetime = models.DateTimeField()


class ObservationCoding(models.Model):
    """ObservationCoding."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_observationcoding_001"

    dbid = models.BigIntegerField(primary_key=True)
    system = models.CharField()
    version = models.CharField()
    code = models.CharField()
    display = models.CharField()
    user_selected = models.BooleanField()
    observation = models.ForeignKey(
        Observation, on_delete=models.DO_NOTHING, related_name="codings", null=True
    )


class ObservationComponent(models.Model):
    """ObservationComponent."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_observationcomponent_001"

    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    observation = models.ForeignKey(
        Observation, on_delete=models.DO_NOTHING, related_name="components", null=True
    )
    value_quantity = models.TextField()
    value_quantity_unit = models.TextField()
    name = models.TextField()


class ObservationComponentCoding(models.Model):
    """ObservationComponentCoding."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_observationcomponentcoding_001"

    dbid = models.BigIntegerField(primary_key=True)
    system = models.CharField()
    version = models.CharField()
    code = models.CharField()
    display = models.CharField()
    user_selected = models.BooleanField()
    observation_component = models.ForeignKey(
        ObservationComponent, on_delete=models.DO_NOTHING, related_name="codings", null=True
    )


class ObservationValueCoding(models.Model):
    """ObservationValueCoding."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_observationvaluecoding_001"

    dbid = models.BigIntegerField(primary_key=True)
    system = models.CharField()
    version = models.CharField()
    code = models.CharField()
    display = models.CharField()
    user_selected = models.BooleanField()
    observation = models.ForeignKey(
        Observation, on_delete=models.DO_NOTHING, related_name="value_codings", null=True
    )


__exports__ = (
    "Observation",
    "ObservationCoding",
    "ObservationComponent",
    "ObservationComponentCoding",
    "ObservationValueCoding",
)
