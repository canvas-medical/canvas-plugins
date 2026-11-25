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


class BusinessLineSetting(TimestampedModel):
    """A business line setting.

    Readable names are ``appointmentReminders`` (``{"daysAhead": int, "hourOfDay": int}``) and
    ``appointmentReminderCustomization`` (the text added to reminder messages); other
    business line settings are not exposed.

    Canvas uses a business line's ``appointmentReminderCustomization`` in place of the
    organization's when business lines are enabled, the business line is active, the reminder
    is for one of its patients, and the business line's value is not empty; otherwise the
    organization's text is used. The text may hold ``{{...}}`` template variables that
    Canvas fills in when it sends. The reminder schedule always comes from the organization's
    ``appointmentReminders``.
    """

    class Meta:
        db_table = "canvas_sdk_data_api_businesslinesetting_001"

    business_line = models.ForeignKey(
        BusinessLine, on_delete=models.DO_NOTHING, related_name="settings"
    )
    name = models.CharField(max_length=100)
    value = models.JSONField(default=dict)


__exports__ = (
    "BusinessLineState",
    "BusinessLine",
    "BusinessLineSetting",
)
