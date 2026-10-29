from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel


class PortalInvitationStatus(models.TextChoices):
    """Where a portal invitation link is in its life. Claimed outranks expired, and expired outranks opened."""

    PENDING = "pending", "Pending"
    OPENED = "opened", "Opened"
    CLAIMED = "claimed", "Claimed"
    EXPIRED = "expired", "Expired"


class PortalInvitationRejectionReason(models.TextChoices):
    """Why the portal refused a click on an invitation link."""

    EXPIRED = "expired", "Expired"
    DIFFERENT_ACCOUNT = "different_account", "Different account"


class PortalInvitation(TimestampedModel, IdentifiableModel):
    """A portal invite or password reset link minted for a user.

    The link itself, its token, and the IP address that opened it stay inside Canvas.
    `first_opened_at` records the first click that worked. A refused click sets only the
    rejection fields. `claimed_at` is set when the link is used to set a password, and links
    minted before claims were recorded show `expired` once spent.
    """

    class Meta:
        db_table = "canvas_sdk_data_app_portal_invitation_001"

    user = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, related_name="portal_invitations"
    )
    expires_at = models.DateTimeField()
    first_opened_at = models.DateTimeField(null=True)
    first_opened_user_agent = models.CharField(max_length=500, null=True)
    claimed_at = models.DateTimeField(null=True)
    last_rejected_at = models.DateTimeField(null=True)
    last_rejection_reason = models.CharField(
        max_length=32, choices=PortalInvitationRejectionReason.choices, null=True
    )
    status = models.CharField(max_length=16, choices=PortalInvitationStatus.choices)
    is_redeemable = models.BooleanField()


__exports__ = ("PortalInvitation", "PortalInvitationRejectionReason", "PortalInvitationStatus")
