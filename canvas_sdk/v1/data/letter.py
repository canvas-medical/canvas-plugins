from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel


class Language(TimestampedModel):
    """Language model for letter templates and staff."""

    class Meta:
        db_table = "canvas_sdk_data_api_language_001"

    code = models.CharField(max_length=3)
    description = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.code


class Letter(TimestampedModel, IdentifiableModel):
    """Letter model for patient correspondence."""

    class Meta:
        db_table = "canvas_sdk_data_api_letter_001"

    content = models.TextField()
    printed = models.DateTimeField(null=True, blank=True)
    note = models.OneToOneField("v1.Note", on_delete=models.CASCADE, related_name="letter")
    staff = models.ForeignKey(
        "v1.Staff", on_delete=models.SET_NULL, related_name="letters", null=True
    )


class EventTypeChoices(models.TextChoices):
    """Choices for types of events that can occur on a letter."""

    PRINTED = "PRINTED", "Printed"
    FAXED = "FAXED", "Faxed"


class LetterActionEvent(TimestampedModel, IdentifiableModel):
    """Event representing an action taken on a letter."""

    class Meta:
        db_table = "canvas_sdk_data_api_letteractionevent_001"

    event_type = models.CharField(max_length=10, choices=EventTypeChoices.choices)
    send_fax_id = models.CharField(max_length=64, blank=True)
    received_by_fax = models.BooleanField(null=True)
    delivered_by_fax = models.BooleanField(null=True)
    fax_result_msg = models.TextField(blank=True)
    originator = models.ForeignKey(
        "v1.CanvasUser", null=True, blank=True, on_delete=models.SET_NULL
    )
    letter = models.ForeignKey(
        "v1.Letter", on_delete=models.CASCADE, related_name="letter_action_events"
    )


__exports__ = (
    "Language",
    "Letter",
    "LetterActionEvent",
)
