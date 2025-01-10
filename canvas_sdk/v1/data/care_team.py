from django.db import models


class CareTeamRole(models.Model):
    """CareTeamRole."""

    dbid = models.BigIntegerField(primary_key=True)
    system = models.CharField()
    version = models.CharField()
    code = models.CharField()
    display = models.CharField()
    user_selected = models.BooleanField()
    active = models.BooleanField()


class CareTeamMembership(models.Model):
    """CareTeamMembership."""

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    patient = models.ForeignKey(
        "Patient", on_delete=models.DO_NOTHING, related_name="care_team_memberships"
    )
    staff = models.ForeignKey(
        "Staff", on_delete=models.DO_NOTHING, related_name="care_team_memberships"
    )
