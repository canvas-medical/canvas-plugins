from django.db import models


class CareTeamMembershipStatus(models.TextChoices):
    """CareTeamMembershipStatus."""

    PROPOSED = "proposed", "Proposed"
    ACTIVE = "active", "Active"
    SUSPENDED = "suspended", "Suspended"
    INACTIVE = "inactive", "Inactive"
    ENTERED_IN_ERROR = "entered-in-error", "Entered in Error"


class CareTeamRole(models.Model):
    """CareTeamRole."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_careteamrole_001"

    dbid = models.BigIntegerField(primary_key=True)
    system = models.CharField()
    version = models.CharField()
    code = models.CharField()
    display = models.CharField()
    user_selected = models.BooleanField()
    active = models.BooleanField()

    def __str__(self) -> str:
        return self.display


class CareTeamMembership(models.Model):
    """CareTeamMembership."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_careteammembership_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="care_team_memberships", null=True
    )
    staff = models.ForeignKey(
        "v1.Staff", on_delete=models.DO_NOTHING, related_name="care_team_memberships", null=True
    )
    role = models.ForeignKey(
        "v1.CareTeamRole", related_name="care_teams", on_delete=models.DO_NOTHING, null=True
    )
    status = models.CharField(choices=CareTeamMembershipStatus.choices)
    lead = models.BooleanField()
    role_code = models.CharField()
    role_system = models.CharField()
    role_display = models.CharField()

    def __str__(self) -> str:
        return f"id={self.id}"


__exports__ = (
    "CareTeamMembershipStatus",
    "CareTeamRole",
    "CareTeamMembership",
)
