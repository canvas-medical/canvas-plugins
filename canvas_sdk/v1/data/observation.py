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


class ObservationQuerySet(
    ValueSetLookupQuerySet, CommittableQuerySetMixin, ForPatientQuerySetMixin
):
    """ObservationQuerySet."""

    pass


ObservationManager = BaseModelManager.from_queryset(ObservationQuerySet)


class Observation(IdentifiableModel):
    """Observation."""

    class Meta:
        db_table = "canvas_sdk_data_api_observation_001"

    objects = cast(ObservationQuerySet, ObservationManager())

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    originator = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    committer = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    entered_in_error = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    deleted = models.BooleanField()
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="observations", null=True
    )
    is_member_of = models.ForeignKey(
        "self", on_delete=models.DO_NOTHING, related_name="members", null=True
    )
    category = models.CharField(max_length=14)
    units = models.TextField()
    value = models.TextField()
    note_id = models.BigIntegerField()
    name = models.TextField()
    effective_datetime = models.DateTimeField()


class ObservationCoding(Model):
    """ObservationCoding."""

    class Meta:
        db_table = "canvas_sdk_data_api_observationcoding_001"

    system = models.CharField(max_length=255)
    version = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    display = models.CharField(max_length=1000)
    user_selected = models.BooleanField()
    observation = models.ForeignKey(
        Observation, on_delete=models.DO_NOTHING, related_name="codings", null=True
    )


class ObservationComponent(Model):
    """ObservationComponent."""

    class Meta:
        db_table = "canvas_sdk_data_api_observationcomponent_001"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    observation = models.ForeignKey(
        Observation, on_delete=models.DO_NOTHING, related_name="components", null=True
    )
    value_quantity = models.TextField()
    value_quantity_unit = models.TextField()
    name = models.TextField()


class ObservationComponentCoding(Model):
    """ObservationComponentCoding."""

    class Meta:
        db_table = "canvas_sdk_data_api_observationcomponentcoding_001"

    system = models.CharField(max_length=255)
    version = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    display = models.CharField(max_length=1000)
    user_selected = models.BooleanField()
    observation_component = models.ForeignKey(
        ObservationComponent, on_delete=models.DO_NOTHING, related_name="codings", null=True
    )


class ObservationValueCoding(Model):
    """ObservationValueCoding."""

    class Meta:
        db_table = "canvas_sdk_data_api_observationvaluecoding_001"

    system = models.CharField(max_length=255)
    version = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    display = models.CharField(max_length=1000)
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
