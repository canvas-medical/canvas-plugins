from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel
from canvas_sdk.v1.data.coding import Coding


class CareTeamMembershipStatus(models.TextChoices):
    """CareTeamMembershipStatus."""

    PROPOSED = "proposed", "Proposed"
    ACTIVE = "active", "Active"
    SUSPENDED = "suspended", "Suspended"
    INACTIVE = "inactive", "Inactive"
    ENTERED_IN_ERROR = "entered-in-error", "Entered in Error"


class CareTeamRole(Coding):
    """CareTeamRole."""

    class Meta:
        db_table = "canvas_sdk_data_api_careteamrole_001"

    active = models.BooleanField()

    def __str__(self) -> str:
        return self.display


class CareTeamMembership(TimestampedModel, IdentifiableModel):
    """CareTeamMembership."""

    class Meta:
        db_table = "canvas_sdk_data_api_careteammembership_001"

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="care_team_memberships", null=True
    )
    staff = models.ForeignKey(
        "v1.Staff", on_delete=models.DO_NOTHING, related_name="care_team_memberships", null=True
    )
    role = models.ForeignKey(
        "v1.CareTeamRole", related_name="care_teams", on_delete=models.DO_NOTHING, null=True
    )
    status = models.CharField(choices=CareTeamMembershipStatus.choices, max_length=20)
    lead = models.BooleanField()
    role_code = models.CharField(max_length=255)
    role_system = models.CharField(max_length=255)
    role_display = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"id={self.id}"


__exports__ = (
    "CareTeamMembershipStatus",
    "CareTeamRole",
    "CareTeamMembership",
)
