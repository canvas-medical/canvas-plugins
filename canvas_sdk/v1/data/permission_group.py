from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel


class PermissionGroup(TimestampedModel, IdentifiableModel):
    """A named permission group (one or more granted to a Role)."""

    class Meta:
        db_table = "canvas_sdk_data_api_permissiongroup_001"

    name = models.CharField(max_length=255)
    internal_code = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=512, blank=True, default="")


class RolePermissionGroup(TimestampedModel):
    """Through-row attaching a PermissionGroup to a Role."""

    class Meta:
        db_table = "canvas_sdk_data_api_rolepermissiongroup_001"

    role = models.ForeignKey(
        "v1.Role",
        on_delete=models.DO_NOTHING,
        related_name="role_permission_groups",
    )
    permission_group = models.ForeignKey(
        PermissionGroup,
        on_delete=models.DO_NOTHING,
        related_name="role_permission_groups",
    )


__exports__ = ("PermissionGroup", "RolePermissionGroup")
