from django.contrib.postgres.fields import ArrayField
from django.db import models

from canvas_sdk.v1.data.action_event_base import BaseActionEvent
from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel
from canvas_sdk.v1.data.utils import presigned_url


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
    printed_document = models.FileField(null=True)

    @property
    def printed_document_url(self) -> str | None:
        """Return a presigned URL for the printed attachments PDF, or None if unset."""
        if self.printed_document:
            return presigned_url(self.printed_document.name)
        return None


class LetterActionEvent(BaseActionEvent):
    """Event representing an action taken on a letter."""

    class Meta:
        db_table = "canvas_sdk_data_api_letteractionevent_001"

    letter = models.ForeignKey(
        "v1.Letter", on_delete=models.CASCADE, related_name="letter_action_events"
    )


class LetterTemplateType(models.TextChoices):
    """The category a letter template belongs to."""

    INTERVENTION = "intervention", "Intervention"
    LETTER = "letter", "Letter"
    MESSAGE = "message", "Message"


class LetterTemplate(TimestampedModel):
    """A reusable letter template, with its categories, locations, and per-language content."""

    class Meta:
        db_table = "canvas_sdk_data_api_lettertemplate_001"

    name = models.CharField(max_length=255)
    active = models.BooleanField()
    restrict_editing = models.BooleanField()
    template_type = ArrayField(
        base_field=models.CharField(max_length=64, choices=LetterTemplateType.choices),
        default=list,
        blank=True,
    )
    locations = ArrayField(base_field=models.CharField(max_length=10), default=list, blank=True)


class LetterLanguageTemplate(TimestampedModel):
    """The header, body, and footer of a letter template in a single language."""

    class Meta:
        db_table = "canvas_sdk_data_api_letterlanguagetemplate_001"

    template = models.ForeignKey(
        "v1.LetterTemplate", on_delete=models.DO_NOTHING, related_name="template_languages"
    )
    header = models.TextField(blank=True, default="")
    content = models.TextField()
    footer = models.TextField(blank=True, default="")
    language = models.ForeignKey(
        "v1.Language", on_delete=models.DO_NOTHING, related_name="letter_language_templates"
    )


__exports__ = (
    "Language",
    "Letter",
    "LetterActionEvent",
    "LetterLanguageTemplate",
    "LetterTemplate",
    "LetterTemplateType",
)
