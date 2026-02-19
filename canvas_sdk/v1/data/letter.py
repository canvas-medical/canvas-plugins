from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, Model, TimestampedModel


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


class LetterActionEvent(Model):
    """Event representing an action taken on a letter."""

    class Meta:
        db_table = "canvas_sdk_data_api_letteractionevent_001"

    letter = models.ForeignKey(
        Letter, on_delete=models.CASCADE, related_name="letter_action_events"
    )


__exports__ = (
    "Language",
    "Letter",
    "LetterActionEvent",
)
