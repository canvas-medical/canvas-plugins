from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, Model, TimestampedModel
from canvas_sdk.v1.data.staff import StaffRole


class AuthGroup(Model):
    """An auth group that grants a set of permissions."""

    class Meta:
        db_table = "canvas_sdk_data_auth_group_001"

    name = models.CharField(max_length=150)


class Role(TimestampedModel, IdentifiableModel):
    """A role that can be assigned to staff."""

    class Meta:
        db_table = "canvas_sdk_data_api_role_001"

    internal_code = models.CharField(max_length=10)
    public_abbreviation = models.CharField(max_length=10, default="", blank=True)
    domain = models.CharField(max_length=3, choices=StaffRole.RoleDomain.choices)
    name = models.CharField(max_length=128)
    domain_privilege_level = models.IntegerField(default=0)
    permissions = models.JSONField(default=dict, blank=True, null=True)
    role_type = models.CharField(max_length=50, choices=StaffRole.RoleType.choices, blank=True)


class RoleGroup(IdentifiableModel):
    """The auth groups a role assigns to new staff created with it."""

    class Meta:
        db_table = "canvas_sdk_data_api_rolegroup_001"

    role = models.ForeignKey(Role, on_delete=models.DO_NOTHING, related_name="role_groups")
    groups = models.ManyToManyField(
        AuthGroup, related_name="role_groups", through="v1.RoleGroupGroup"
    )


class RoleGroupGroup(Model):
    """M2M for RoleGroup -> AuthGroup."""

    class Meta:
        db_table = "canvas_sdk_data_api_rolegroup_groups_001"

    role_group = models.ForeignKey(
        RoleGroup, on_delete=models.DO_NOTHING, db_column="rolegroup_id", related_name="+"
    )
    group = models.ForeignKey(AuthGroup, on_delete=models.DO_NOTHING, related_name="+")


__exports__ = ("AuthGroup", "Role", "RoleGroup", "RoleGroupGroup")
