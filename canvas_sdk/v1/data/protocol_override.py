from django.db import models
from django.utils.translation import gettext_lazy as _

from canvas_sdk.v1.data.base import CommittableModelManager
from canvas_sdk.v1.data.patient import Patient
from canvas_sdk.v1.data.user import CanvasUser


class IntervalUnit(models.TextChoices):
    """ProtocolOverride cycle IntervalUnit."""

    DAYS = "days", _("days")
    MONTHS = "months", _("months")
    YEARS = "years", _("years")


class Status(models.TextChoices):
    """ProtocolOverride Status."""

    ACTIVE = "active", _("active")
    INACTIVE = "inactive", _("inactive")


class ProtocolOverride(models.Model):
    """ProtocolOverride."""

    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_protocoloverride_001"

    objects = CommittableModelManager()

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    deleted = models.BooleanField()
    committer = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING)
    entered_in_error = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING)
    patient = models.ForeignKey(
        Patient,
        on_delete=models.DO_NOTHING,
        related_name="allergy_intolerances",
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
