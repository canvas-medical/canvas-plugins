from django.db import models

from canvas_sdk.v1.data.base import TimestampedModel


class StaffIdentityVerification(TimestampedModel):
    """One completed ID.me identity proofing of a staff member.

    A staff member can be proofed more than once, so "verified" means at least one row
    exists; rows are ordered newest ``verified_at`` first.
    """

    class Meta:
        db_table = "canvas_sdk_data_api_staffidentityverification_001"
        ordering = ("-verified_at",)

    staff = models.ForeignKey(
        "v1.Staff", on_delete=models.DO_NOTHING, related_name="identity_verifications"
    )
    verified_at = models.DateTimeField()
    # The ID.me policy (assurance level) the proofing satisfied.
    policy_scope = models.CharField(max_length=255)
    # True when the name ID.me verified differed from the staff record (the birth date
    # matched, so the proofing stands). The staff record's name likely needs updating.
    name_mismatch = models.BooleanField()


__exports__ = ("StaffIdentityVerification",)
