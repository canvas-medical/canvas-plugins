from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel


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
    fax = models.ForeignKey(
        "v1.Fax", null=True, blank=True, on_delete=models.SET_NULL, related_name="%(class)ss"
    )


__exports__ = ()
