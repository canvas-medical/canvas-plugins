from django.db import models


class BusinessLineState(models.TextChoices):
    """BusinessLineStatus."""

    STATE_SUCCESS = "success", "Success"
    STATE_PENDING = "pending", "Pending"
    STATE_ERROR = "error", "Deleted"


class BusinessLine(models.Model):
    """Business Line."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_businessline_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    name = models.CharField()
    description = models.TextField()
    area_code = models.CharField()
    subdomain = models.CharField()
    active = models.BooleanField()
    state = models.CharField(max_length=20, choices=BusinessLineState)
    organization = models.ForeignKey(
        "v1.Organization", on_delete=models.DO_NOTHING, related_name="business_lines"
    )


__exports__ = (
    "BusinessLineState",
    "BusinessLine",
)
