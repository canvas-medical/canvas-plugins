from django.db import models

from canvas_sdk.v1.data.base import TimestampedModel
from canvas_sdk.v1.data.staff import StaffRole


class RoleType(models.TextChoices):
    """Licensing tier of a Role."""

    NON_LICENSED = "NON-LICENSED", "Non-Licensed"
    LICENSED = "LICENSED", "Licensed"
    PROVIDER = "PROVIDER", "Provider"


class Role(TimestampedModel):
    """A staff role definition (Physician / Nurse / Front Desk / etc.)."""

    class Meta:
        db_table = "canvas_sdk_data_api_role_001"

    internal_code = models.CharField(max_length=10, unique=True)
    public_abbreviation = models.CharField(max_length=10, blank=True, default="")
    domain = models.CharField(max_length=3, choices=StaffRole.RoleDomain.choices)
    name = models.CharField(max_length=128)
    domain_privilege_level = models.IntegerField(default=0)
    role_type = models.CharField(max_length=50, choices=RoleType.choices, blank=True)


__exports__ = ("Role", "RoleType")
