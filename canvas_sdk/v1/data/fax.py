from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel


class FaxDirection(models.TextChoices):
    """Whether a fax was sent or received."""

    OUTBOUND = "O", "Outbound"
    INBOUND = "I", "Inbound"


class Fax(TimestampedModel, IdentifiableModel):
    """A fax sent or received through the Canvas faxing service."""

    class Meta:
        db_table = "canvas_sdk_data_data_integration_fax_001"

    fax_id = models.CharField(max_length=255, null=True, db_index=True)
    to_fax_number = models.CharField(max_length=16, default="", blank=True)
    from_fax_number = models.CharField(max_length=16, default="", blank=True)
    date_utc = models.DateTimeField(null=True)
    fax_pages = models.IntegerField(null=True)
    direction = models.CharField(max_length=1, choices=FaxDirection.choices)
    success = models.BooleanField(default=False)


class FaxStatus(models.TextChoices):
    """The status recorded for a fax."""

    PROCESSING = "P", "Processing"
    SENT = "S", "Sent"
    RECEIVED = "R", "Received"
    ERROR = "E", "Error"


class FaxStatusModel(TimestampedModel, IdentifiableModel):
    """A status recorded for a fax."""

    class Meta:
        db_table = "canvas_sdk_data_data_integration_faxstatusmodel_001"

    fax = models.ForeignKey("v1.Fax", on_delete=models.CASCADE, related_name="fax_statuses")
    status = models.CharField(max_length=1, choices=FaxStatus.choices, db_index=True)


class EventTypeChoices(models.TextChoices):
    """Choices for types of events that can occur on a document."""

    PRINTED = "PRINTED", "Printed"
    FAXED = "FAXED", "Faxed"


class BaseActionEvent(TimestampedModel, IdentifiableModel):
    """Abstract base for a print or fax action taken on a document."""

    class Meta:
        abstract = True

    event_type = models.CharField(max_length=10, choices=EventTypeChoices.choices)
    send_fax_id = models.CharField(max_length=64, blank=True)
    received_by_fax = models.BooleanField(null=True)
    delivered_by_fax = models.BooleanField(null=True)
    fax_result_msg = models.TextField(blank=True)
    originator = models.ForeignKey(
        "v1.CanvasUser", null=True, blank=True, on_delete=models.SET_NULL
    )
    fax = models.ForeignKey("v1.Fax", null=True, blank=True, on_delete=models.SET_NULL)


__exports__ = (
    "Fax",
    "FaxDirection",
    "FaxStatus",
    "FaxStatusModel",
)
