from typing import cast

from django.db import models
from django.utils import timezone

from canvas_sdk.v1.data.base import (
    AuditedModel,
    BaseModelManager,
    BaseQuerySet,
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
    IdentifiableModel,
    TimestampedModel,
)


class VitalSignReadingQuerySet(
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
    BaseQuerySet,
):
    """VitalSignReadingQuerySet."""

    pass


VitalSignReadingManager = BaseModelManager.from_queryset(VitalSignReadingQuerySet)


class VitalSignReading(AuditedModel, IdentifiableModel):
    """The anchor for a vitals command — a set of readings recorded on a note for a patient."""

    class Meta:
        db_table = "canvas_sdk_data_api_vitalsignreading_001"

    objects = cast(VitalSignReadingQuerySet, VitalSignReadingManager())

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="vital_sign_readings"
    )
    note = models.ForeignKey(
        "v1.Note", on_delete=models.DO_NOTHING, related_name="vital_sign_readings"
    )
    date_recorded = models.DateTimeField()


class VitalSign(TimestampedModel, IdentifiableModel):
    """A single vital-sign measurement (e.g. blood pressure) belonging to a VitalSignReading."""

    class Meta:
        db_table = "canvas_sdk_data_api_vitalsign_001"

    reading = models.ForeignKey(VitalSignReading, on_delete=models.DO_NOTHING, related_name="signs")
    date_recorded = models.DateTimeField(default=timezone.now, db_index=True)
    loinc_num = models.CharField(max_length=10)
    sign = models.CharField(max_length=33)
    sign_description = models.CharField(max_length=100, blank=True, default="")
    value = models.CharField(max_length=150)
    units = models.CharField(max_length=50, blank=True, default="")
    source = models.CharField(max_length=255, blank=True, default="")
    parent = models.ForeignKey(
        "self", on_delete=models.DO_NOTHING, null=True, related_name="children"
    )


__exports__ = ("VitalSign", "VitalSignReading")
