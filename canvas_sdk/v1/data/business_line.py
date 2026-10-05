from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel
from canvas_sdk.v1.data.utils import presigned_url


class BusinessLineState(models.TextChoices):
    """BusinessLineStatus."""

    STATE_SUCCESS = "success", "Success"
    STATE_PENDING = "pending", "Pending"
    STATE_ERROR = "error", "Deleted"


class BusinessLine(TimestampedModel, IdentifiableModel):
    """Business Line."""

    class Meta:
        db_table = "canvas_sdk_data_api_businessline_001"

    name = models.CharField(max_length=255)
    description = models.TextField()
    area_code = models.CharField(max_length=3)
    subdomain = models.CharField(max_length=100)
    active = models.BooleanField()
    state = models.CharField(max_length=20, choices=BusinessLineState.choices)
    organization = models.ForeignKey(
        "v1.Organization", on_delete=models.DO_NOTHING, related_name="business_lines"
    )
    logo = models.FileField(blank=False)

    @property
    def logo_url(self) -> str | None:
        """Return a presigned URL for the logo image, or None if unset."""
        if self.logo:
            return presigned_url(self.logo.name)
        return None


__exports__ = (
    "BusinessLineState",
    "BusinessLine",
)
