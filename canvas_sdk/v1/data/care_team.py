from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, Model


class CareTeamMembershipStatus(models.TextChoices):
    """CareTeamMembershipStatus."""

    PROPOSED = "proposed", "Proposed"
    ACTIVE = "active", "Active"
    SUSPENDED = "suspended", "Suspended"
    INACTIVE = "inactive", "Inactive"
    ENTERED_IN_ERROR = "entered-in-error", "Entered in Error"


class CareTeamRole(Model):
    """CareTeamRole."""

    class Meta:
        db_table = "canvas_sdk_data_api_careteamrole_001"

    system = models.CharField(max_length=255)
    version = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    display = models.CharField(max_length=1000)
    user_selected = models.BooleanField()
    active = models.BooleanField()

    def __str__(self) -> str:
        return self.display


class CareTeamMembership(IdentifiableModel):
    """CareTeamMembership."""

    class Meta:
        db_table = "canvas_sdk_data_api_careteammembership_001"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
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
