from typing import cast

from django.db import models

from canvas_sdk.v1.data.base import (
    AuditedModel,
    BaseModelManager,
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
    IdentifiableModel,
    TimestampedModel,
    ValueSetLookupQuerySet,
)
from canvas_sdk.v1.data.coding import Coding


class ObservationQuerySet(
    ValueSetLookupQuerySet, CommittableQuerySetMixin, ForPatientQuerySetMixin
):
    """ObservationQuerySet."""

    pass


ObservationManager = BaseModelManager.from_queryset(ObservationQuerySet)


class Observation(AuditedModel, IdentifiableModel):
    """Observation."""

    class Meta:
        db_table = "canvas_sdk_data_api_observation_001"

    objects = cast(ObservationQuerySet, ObservationManager())

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


class ObservationCoding(Coding):
    """ObservationCoding."""

    class Meta:
        db_table = "canvas_sdk_data_api_observationcoding_001"

    observation = models.ForeignKey(
        Observation, on_delete=models.DO_NOTHING, related_name="codings", null=True
    )


class ObservationComponent(TimestampedModel):
    """ObservationComponent."""

    class Meta:
        db_table = "canvas_sdk_data_api_observationcomponent_001"

    observation = models.ForeignKey(
        Observation, on_delete=models.DO_NOTHING, related_name="components", null=True
    )
    value_quantity = models.TextField()
    value_quantity_unit = models.TextField()
    name = models.TextField()


class ObservationComponentCoding(Coding):
    """ObservationComponentCoding."""

    class Meta:
        db_table = "canvas_sdk_data_api_observationcomponentcoding_001"

    observation_component = models.ForeignKey(
        ObservationComponent, on_delete=models.DO_NOTHING, related_name="codings", null=True
    )


class ObservationValueCoding(Coding):
    """ObservationValueCoding."""

    class Meta:
        db_table = "canvas_sdk_data_api_observationvaluecoding_001"

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
