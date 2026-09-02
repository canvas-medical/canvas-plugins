from django.db import models
from django.db.models.enums import TextChoices

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel


class RoleDomain(TextChoices):
    """Mirrors api.Role.DOMAIN_CHOICES."""

    CLINICAL = "CLI", "Clinical"
    ADMINISTRATIVE = "ADM", "Administrative"
    HYBRID = "HYB", "Hybrid"


class Role(TimestampedModel, IdentifiableModel):
    """A staff role (Physician / Nurse / Front Desk / etc.)."""

    class Meta:
        db_table = "canvas_sdk_data_api_role_001"

    name = models.CharField(max_length=255)
    internal_code = models.CharField(max_length=64, unique=True)
    public_abbreviation = models.CharField(max_length=32, blank=True, default="")
    domain = models.CharField(max_length=3, choices=RoleDomain.choices)
    domain_privilege_level = models.IntegerField(default=0)


__exports__ = ("Role", "RoleDomain")
