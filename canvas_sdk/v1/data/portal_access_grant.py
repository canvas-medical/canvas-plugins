from typing import Any

from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel
from canvas_sdk.v1.portal_access_level import PortalAccessLevel

_PORTAL_ACCESS_LEVEL_CHOICES = [(level.value, level.name.title()) for level in PortalAccessLevel]


class _PortalAccessLevelField(models.CharField):
    """A level loaded as a PortalAccessLevel, so it compares by how much it allows."""

    def from_db_value(
        self, value: str | None, expression: Any, connection: Any
    ) -> PortalAccessLevel | None:
        # None when an outer join finds no grant, e.g. values("portal_grants__clinical").
        return None if value is None else PortalAccessLevel(value)


class PortalAccessGrant(TimestampedModel, IdentifiableModel):
    """
    A portal login's access to a patient's chart that isn't its own, such as a parent's to a child's.

    Staff give it from one of the patient's contacts. Its level in each area, appointments,
    messaging, clinical and billing, is "none" (hide the area), "view" (show it read-only) or "act"
    (allow its actions too), read as a PortalAccessLevel so it compares by how much it allows.
    Revoked and flagged grants stay as history: only a grant that is neither, on an active
    patient, gives the login the chart.
    """

    class Meta:
        db_table = "canvas_sdk_data_api_portalaccessgrant_001"

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="portal_grants"
    )
    user = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, related_name="portal_grants"
    )
    # Cleared when the contact is deleted; contact_name and contact_relationship keep its history.
    contact = models.ForeignKey(
        "v1.PatientContactPerson",
        on_delete=models.DO_NOTHING,
        related_name="portal_grants",
        null=True,
        blank=True,
    )
    contact_name = models.CharField(max_length=255, blank=True, default="")
    contact_relationship = models.CharField(max_length=255, blank=True, default="")

    appointments = _PortalAccessLevelField(
        max_length=4, choices=_PORTAL_ACCESS_LEVEL_CHOICES, default=PortalAccessLevel.ACT
    )
    messaging = _PortalAccessLevelField(
        max_length=4, choices=_PORTAL_ACCESS_LEVEL_CHOICES, default=PortalAccessLevel.ACT
    )
    clinical = _PortalAccessLevelField(
        max_length=4, choices=_PORTAL_ACCESS_LEVEL_CHOICES, default=PortalAccessLevel.ACT
    )
    billing = _PortalAccessLevelField(
        max_length=4, choices=_PORTAL_ACCESS_LEVEL_CHOICES, default=PortalAccessLevel.ACT
    )

    dob_verified_at = models.DateTimeField(null=True, blank=True)
    dob_failed_attempts = models.PositiveSmallIntegerField(default=0)
    # Set when the login said "I don't know this person".
    flagged_at = models.DateTimeField(null=True, blank=True)

    granted_by = models.ForeignKey("v1.Staff", on_delete=models.DO_NOTHING, related_name="+")
    granted_at = models.DateTimeField(auto_now_add=True)
    notified_at = models.DateTimeField(null=True, blank=True)

    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_by = models.ForeignKey(
        "v1.Staff", on_delete=models.DO_NOTHING, related_name="+", null=True, blank=True
    )
    revoke_reason = models.TextField(blank=True, default="")


__exports__ = ("PortalAccessGrant", "PortalAccessLevel")
