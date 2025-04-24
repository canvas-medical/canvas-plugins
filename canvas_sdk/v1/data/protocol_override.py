from typing import cast

from django.db import models

from canvas_sdk.v1.data.base import (
    BaseModelManager,
    BaseQuerySet,
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
)


class IntervalUnit(models.TextChoices):
    """ProtocolOverride cycle IntervalUnit."""

    DAYS = "days", "days"
    MONTHS = "months", "months"
    YEARS = "years", "years"


class Status(models.TextChoices):
    """ProtocolOverride Status."""

    ACTIVE = "active", "active"
    INACTIVE = "inactive", "inactive"


class ProtocolOverrideQuerySet(BaseQuerySet, ForPatientQuerySetMixin, CommittableQuerySetMixin):
    """ProtocolOverrideQuerySet."""

    pass


ProtocolOverrideManager = BaseModelManager.from_queryset(ProtocolOverrideQuerySet)


class ProtocolOverride(models.Model):
    """ProtocolOverride."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_protocoloverride_001"

    objects = cast(ProtocolOverrideQuerySet, ProtocolOverrideManager())

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    deleted = models.BooleanField()
    committer = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, null=True)
    entered_in_error = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, null=True)
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="protocol_overrides", null=True
    )
    protocol_key = models.CharField()
    is_adjustment = models.BooleanField()
    reference_date = models.DateTimeField()
    cycle_in_days = models.IntegerField()
    is_snooze = models.BooleanField()
    snooze_date = models.DateField()
    snoozed_days = models.IntegerField()
    # reason_id = models.BigIntegerField()
    snooze_comment = models.TextField()
    narrative = models.CharField()
    # note_id = models.BigIntegerField()
    cycle_quantity = models.IntegerField()
    cycle_unit = models.CharField(choices=IntervalUnit.choices)
    status = models.CharField(choices=Status.choices)


__exports__ = (
    "IntervalUnit",
    "Status",
    "ProtocolOverride",
)
