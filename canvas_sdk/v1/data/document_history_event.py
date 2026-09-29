from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel


class DocumentHistoryEventType(models.TextChoices):
    """The kinds of entries in a reviewable document's history."""

    REASSIGNED = "reassigned", "Reassigned"
    COMMENTED = "commented", "Commented"
    RELEASED = "released", "Released signature"
    RECORDED = "recorded", "Recorded"
    ENTERED_IN_ERROR = "entered_in_error", "Entered in error"


class DocumentHistoryEvent(TimestampedModel, IdentifiableModel):
    """One entry in a reviewable document's history timeline.

    Covers lab reports, imaging reports, referral reports and uncategorized clinical
    documents. ``content_type`` + ``object_id`` form a generic link to the document;
    ``review_content_type`` + ``review_object_id`` link a "recorded" or "entered in error"
    entry to its review command.

    ``deleted_at`` marks a comment hidden without removing the entry: a "recorded" entry keeps
    its place after its review is entered in error, but its internal comment no longer shows.
    """

    class Meta:
        db_table = "canvas_sdk_data_api_documenthistoryevent_001"

    content_type = models.ForeignKey(
        "v1.ContentType", on_delete=models.DO_NOTHING, related_name="+"
    )
    object_id = models.IntegerField()

    event_type = models.CharField(max_length=32, choices=DocumentHistoryEventType.choices)
    actor = models.ForeignKey("v1.Staff", on_delete=models.DO_NOTHING, related_name="+", null=True)
    recipient_staff = models.ForeignKey(
        "v1.Staff", on_delete=models.DO_NOTHING, related_name="+", null=True
    )
    recipient_team = models.ForeignKey(
        "v1.Team", on_delete=models.DO_NOTHING, related_name="+", null=True
    )
    comment = models.TextField()
    delegation = models.ForeignKey(
        "v1.DocumentReviewDelegation",
        on_delete=models.DO_NOTHING,
        related_name="history_events",
        null=True,
    )
    review_content_type = models.ForeignKey(
        "v1.ContentType", on_delete=models.DO_NOTHING, related_name="+", null=True
    )
    review_object_id = models.IntegerField(null=True)
    signers = models.ManyToManyField(
        "v1.Staff",
        related_name="+",
        db_table="canvas_sdk_data_api_documenthistoryevent_signers_001",
        blank=True,
    )
    deleted_at = models.DateTimeField(null=True)

    @property
    def comment_hidden(self) -> bool:
        """True when the entry's comment was hidden because its review was entered in error."""
        return self.deleted_at is not None


__exports__ = ("DocumentHistoryEvent", "DocumentHistoryEventType")
