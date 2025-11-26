from typing import TYPE_CHECKING, Self, cast

from django.db import models

from canvas_sdk.v1.data.base import (
    BaseModelManager,
    BaseQuerySet,
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
    IdentifiableModel,
    TimestampedModel,
)

if TYPE_CHECKING:
    from canvas_sdk.v1.data.patient import Patient


class IntervalUnit(models.TextChoices):
    """ProtocolOverride cycle IntervalUnit."""

    DAYS = "days", "days"
    MONTHS = "months", "months"
    YEARS = "years", "years"


class Status(models.TextChoices):
    """ProtocolOverride Status."""

    ACTIVE = "active", "active"
    INACTIVE = "inactive", "inactive"


class ProtocolOverrideQuerySet(ForPatientQuerySetMixin, CommittableQuerySetMixin, BaseQuerySet):
    """ProtocolOverrideQuerySet."""

    def active_adjustments(self, protocol_key: str) -> Self:
        """
        Filter to active adjustments for a specific protocol.

        This returns protocol overrides that are:
        - Not deleted
        - Status is ACTIVE
        - is_adjustment is True
        - Matching the given protocol_key

        Results are ordered by most recently modified first.

        Args:
            protocol_key: The protocol identifier (e.g., 'CMS125v14').

        Returns:
            Filtered QuerySet of active adjustments.

        Example:
            >>> from canvas_sdk.v1.data.protocol_override import ProtocolOverride
            >>> overrides = ProtocolOverride.objects.filter(
            ...     patient=patient
            ... ).active_adjustments("CMS125v14")
            >>> latest = overrides.first()
        """
        return self.filter(
            protocol_key=protocol_key,
            deleted=False,
            status=Status.ACTIVE,
            is_adjustment=True,
        ).order_by("-modified")

    def get_active_adjustment(
        self, patient: "Patient", protocol_key: str
    ) -> "ProtocolOverride | None":
        """
        Get the most recent active adjustment for a patient and protocol.

        This is a convenience method that combines filtering for a patient,
        active adjustments for a protocol, and returns the first (most recent) one.

        Args:
            patient: The patient to check.
            protocol_key: The protocol identifier (e.g., 'CMS125v14').

        Returns:
            The most recent active ProtocolOverride adjustment, or None if not found.

        Example:
            >>> from canvas_sdk.v1.data.protocol_override import ProtocolOverride
            >>> override = ProtocolOverride.objects.get_active_adjustment(
            ...     patient=patient,
            ...     protocol_key="CMS125v14"
            ... )
            >>> if override:
            ...     print(f"Custom cycle: {override.cycle_in_days} days")
        """
        return self.filter(patient=patient).active_adjustments(protocol_key).first()


ProtocolOverrideManager = BaseModelManager.from_queryset(ProtocolOverrideQuerySet)


class ProtocolOverride(TimestampedModel, IdentifiableModel):
    """ProtocolOverride."""

    class Meta:
        db_table = "canvas_sdk_data_api_protocoloverride_001"

    objects = cast(ProtocolOverrideQuerySet, ProtocolOverrideManager())

    deleted = models.BooleanField()
    committer = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    entered_in_error = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="protocol_overrides", null=True
    )
    protocol_key = models.CharField(max_length=250)
    is_adjustment = models.BooleanField()
    reference_date = models.DateTimeField()
    cycle_in_days = models.IntegerField()
    is_snooze = models.BooleanField()
    snooze_date = models.DateField()
    snoozed_days = models.IntegerField()
    # reason_id = models.BigIntegerField()
    snooze_comment = models.TextField()
    narrative = models.CharField(max_length=512)
    # note_id = models.BigIntegerField()
    cycle_quantity = models.IntegerField()
    cycle_unit = models.CharField(choices=IntervalUnit.choices, max_length=20)
    status = models.CharField(choices=Status.choices, max_length=20)


__exports__ = (
    "IntervalUnit",
    "Status",
    "ProtocolOverride",
)
