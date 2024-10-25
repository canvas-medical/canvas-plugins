from django.db import models

from canvas_sdk.v1.data.base import CommittableModelManager, ValueSetLookupQuerySet
from canvas_sdk.v1.data.patient import Patient
from canvas_sdk.v1.data.user import CanvasUser


class ObservationQuerySet(ValueSetLookupQuerySet):
    """ObservationQuerySet."""

    pass


class Observation(models.Model):
    """Observation."""

    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_observation_001"

    objects = CommittableModelManager.from_queryset(ObservationQuerySet)()

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    originator = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING)
    committer = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING)
    entered_in_error = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING)
    deleted = models.BooleanField()
    patient = models.ForeignKey(Patient, on_delete=models.DO_NOTHING, related_name="observations")
    is_member_of = models.ForeignKey(
        "self", on_delete=models.DO_NOTHING, null=True, related_name="members"
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
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_observationcoding_001"

    dbid = models.BigIntegerField(primary_key=True)
    system = models.CharField()
    version = models.CharField()
    code = models.CharField()
    display = models.CharField()
    user_selected = models.BooleanField()
    observation = models.ForeignKey(
        Observation, on_delete=models.DO_NOTHING, related_name="codings"
    )


class ObservationComponent(models.Model):
    """ObservationComponent."""

    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_observationcomponent_001"

    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    observation = models.ForeignKey(
        Observation, on_delete=models.DO_NOTHING, related_name="components"
    )
    value_quantity = models.TextField()
    value_quantity_unit = models.TextField()
    name = models.TextField()


class ObservationComponentCoding(models.Model):
    """ObservationComponentCoding."""

    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_observationcomponentcoding_001"

    dbid = models.BigIntegerField(primary_key=True)
    system = models.CharField()
    version = models.CharField()
    code = models.CharField()
    display = models.CharField()
    user_selected = models.BooleanField()
    observation_component = models.ForeignKey(
        ObservationComponent, on_delete=models.DO_NOTHING, related_name="codings"
    )


class ObservationValueCoding(models.Model):
    """ObservationValueCoding."""

    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_observationvaluecoding_001"

    dbid = models.BigIntegerField(primary_key=True)
    system = models.CharField()
    version = models.CharField()
    code = models.CharField()
    display = models.CharField()
    user_selected = models.BooleanField()
    observation = models.ForeignKey(
        Observation, on_delete=models.DO_NOTHING, related_name="value_codings"
    )
