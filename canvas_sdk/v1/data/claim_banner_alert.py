from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel


class BannerAlertStatus(models.TextChoices):
    """BannerAlertStatus."""

    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"


class BannerAlertIntent(models.TextChoices):
    """BannerAlertIntent."""

    INFO = "info", "Info"
    WARNING = "warning", "Warning"
    ALERT = "alert", "Alert"


class ClaimBannerAlert(TimestampedModel, IdentifiableModel):
    """ClaimBannerAlert."""

    class Meta:
        db_table = "canvas_sdk_data_api_claimbanneralert_001"

    claim = models.ForeignKey("v1.Claim", on_delete=models.DO_NOTHING, related_name="banner_alerts")
    plugin_name = models.CharField(max_length=256)
    key = models.CharField(max_length=255)
    narrative = models.CharField(max_length=90)
    intent = models.CharField(max_length=64, choices=BannerAlertIntent.choices)
    href = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(
        max_length=64, choices=BannerAlertStatus.choices, default=BannerAlertStatus.ACTIVE
    )


__exports__ = ("ClaimBannerAlert", "BannerAlertIntent", "BannerAlertStatus")
