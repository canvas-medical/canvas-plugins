from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel


class PortalAccessLevel(models.TextChoices):
    """
    How much a login may do in one area of the patient's chart.

    With NONE, hide the area; with VIEW, show it read-only; with ACT, allow its actions too. Levels
    compare by how much they allow, NONE < VIEW < ACT, and NONE is falsy.
    """

    NONE = "none"
    VIEW = "view"
    ACT = "act"

    def __lt__(self, other: object) -> bool:
        return _rank(self) < _rank(other)

    def __le__(self, other: object) -> bool:
        return _rank(self) <= _rank(other)

    def __gt__(self, other: object) -> bool:
        return _rank(self) > _rank(other)

    def __ge__(self, other: object) -> bool:
        return _rank(self) >= _rank(other)

    def __bool__(self) -> bool:
        return _rank(self) > 0


_PORTAL_ACCESS_RANKS = {
    PortalAccessLevel.NONE: 0,
    PortalAccessLevel.VIEW: 1,
    PortalAccessLevel.ACT: 2,
}


def _rank(level: object) -> int:
    if not isinstance(level, str):
        raise TypeError(f"Cannot compare a portal access level with {type(level).__name__}")
    return _PORTAL_ACCESS_RANKS[PortalAccessLevel(level)]


class PortalAccessGrant(TimestampedModel, IdentifiableModel):
    """
    A portal login's access to a patient's chart that isn't its own, such as a parent's to a child's.

    Staff give it from one of the patient's contacts. Its level in each area, appointments,
    messaging, clinical and billing, is "none" (hide the area), "view" (show it read-only) or "act"
    (allow its actions too); wrap one in PortalAccessLevel to compare it. Revoked and flagged
    grants stay as history: only a grant that is neither, on an active patient, gives the login
    the chart.
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

    appointments = models.CharField(
        max_length=4, choices=PortalAccessLevel.choices, default=PortalAccessLevel.ACT
    )
    messaging = models.CharField(
        max_length=4, choices=PortalAccessLevel.choices, default=PortalAccessLevel.ACT
    )
    clinical = models.CharField(
        max_length=4, choices=PortalAccessLevel.choices, default=PortalAccessLevel.ACT
    )
    billing = models.CharField(
        max_length=4, choices=PortalAccessLevel.choices, default=PortalAccessLevel.ACT
    )

    dob_verified_at = models.DateTimeField(null=True)
    dob_failed_attempts = models.PositiveSmallIntegerField(default=0)
    # Set when the login said "I don't know this person".
    flagged_at = models.DateTimeField(null=True)

    granted_by = models.ForeignKey("v1.Staff", on_delete=models.DO_NOTHING, related_name="+")
    granted_at = models.DateTimeField()
    notified_at = models.DateTimeField(null=True)

    revoked_at = models.DateTimeField(null=True)
    revoked_by = models.ForeignKey(
        "v1.Staff", on_delete=models.DO_NOTHING, related_name="+", null=True
    )
    revoke_reason = models.TextField(blank=True, default="")


__exports__ = ("PortalAccessGrant", "PortalAccessLevel")
