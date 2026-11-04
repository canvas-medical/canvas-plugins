from typing import TypeAlias, TypeVar

from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel
from canvas_sdk.v1.data.django_content_type import ContentType
from canvas_sdk.v1.data.imaging import ImagingReport, ImagingReview
from canvas_sdk.v1.data.lab import LabReport, LabReview
from canvas_sdk.v1.data.referral import ReferralReport, ReferralReview
from canvas_sdk.v1.data.uncategorized_clinical_document import (
    UncategorizedClinicalDocument,
    UncategorizedClinicalDocumentReview,
)

ReviewableDocument: TypeAlias = (
    LabReport | ImagingReport | ReferralReport | UncategorizedClinicalDocument
)
DocumentReview: TypeAlias = (
    LabReview | ImagingReview | ReferralReview | UncategorizedClinicalDocumentReview
)

# The SDK model for each content type a history entry links to, keyed by its model name.
_DOCUMENT_MODELS: dict[str, type[ReviewableDocument]] = {
    "labreport": LabReport,
    "imagingreport": ImagingReport,
    "referralreport": ReferralReport,
    "uncategorizedclinicaldocument": UncategorizedClinicalDocument,
}
_REVIEW_MODELS: dict[str, type[DocumentReview]] = {
    "labreview": LabReview,
    "imagingreview": ImagingReview,
    "referralreview": ReferralReview,
    "uncategorizeddocumentreview": UncategorizedClinicalDocumentReview,
}

_T = TypeVar("_T", bound=models.Model)


def _resolve(
    models_by_name: dict[str, type[_T]], content_type: ContentType | None, object_id: int | None
) -> _T | None:
    """The instance a content type + object id points at, or None for an unknown type."""
    if content_type is None or object_id is None or content_type.app_label != "api":
        return None
    model = models_by_name.get(content_type.model)
    return model._default_manager.filter(dbid=object_id).first() if model else None


class DocumentHistoryEventType(models.TextChoices):
    """The kinds of entries in a reviewable document's history."""

    REASSIGNED = "reassigned", "Reassigned"
    COMMENTED = "commented", "Commented"
    SENT_FOR_SIGNATURE = "sent_for_signature", "Sent for signature"
    SIGNED = "signed", "Signed"
    SIGNATURE_REMOVED = "signature_removed", "Signature removed"
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
    def document(self) -> ReviewableDocument | None:
        """The lab, imaging or referral report, or uncategorized clinical document, of this entry."""
        return _resolve(_DOCUMENT_MODELS, self.content_type, self.object_id)

    @property
    def review(self) -> DocumentReview | None:
        """The review command of a "recorded" or "entered in error" entry, else None."""
        return _resolve(_REVIEW_MODELS, self.review_content_type, self.review_object_id)

    @property
    def comment_hidden(self) -> bool:
        """True when the entry's comment was hidden because its review was entered in error."""
        return self.deleted_at is not None


__exports__ = ("DocumentHistoryEvent", "DocumentHistoryEventType")
