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
    template = models.ForeignKey(
        "v1.LetterLanguageTemplate",
        on_delete=models.SET_NULL,
        related_name="letters",
        null=True,
        blank=True,
    )

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
    """The kind of document a letter template is used for."""

    INTERVENTION = "intervention", "Intervention"
    LETTER = "letter", "Letter"
    MESSAGE = "message", "Message"


class LetterTemplate(TimestampedModel, IdentifiableModel):
    """A reusable letter template, with its kinds, locations and per-language content."""

    class Meta:
        db_table = "canvas_sdk_data_api_lettertemplate_001"

    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    restrict_editing = models.BooleanField(default=False)
    template_type = ArrayField(
        models.CharField(max_length=64, choices=LetterTemplateType.choices),
        blank=True,
        default=list,
    )
    locations = ArrayField(models.CharField(max_length=10, default=""), blank=True, default=list)


class LetterLanguageTemplate(TimestampedModel, IdentifiableModel):
    """The header, content and footer of a letter template in one language."""

    class Meta:
        db_table = "canvas_sdk_data_api_letterlanguagetemplate_001"

    template = models.ForeignKey(
        "v1.LetterTemplate", on_delete=models.DO_NOTHING, related_name="template_languages"
    )
    header = models.TextField(blank=True, default="")
    content = models.TextField()
    footer = models.TextField(blank=True, default="")
    language = models.ForeignKey(
        "v1.Language", on_delete=models.DO_NOTHING, related_name="letter_template_contents"
    )


__exports__ = (
    "Language",
    "Letter",
    "LetterActionEvent",
    "LetterLanguageTemplate",
    "LetterTemplate",
    "LetterTemplateType",
)
