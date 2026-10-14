from django.db import models
from django.db.models.options import Options

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel


class DocumentReviewDelegation(TimestampedModel, IdentifiableModel):
    """A hop of a reviewable document sent for signature, or routed back once signed.

    Append-only log with a single active row per document (``is_active``). Sending a document
    for signature writes a row to the provider, with ``on_behalf_of`` naming the sender; signing
    and returning it writes a route-back to the sender (``is_route_back``). Any other hand-off,
    or the document no longer needing review, deactivates the active row.
    ``signature_consent`` grants nothing: each user places only their own signature. Rows to a
    team are hand-offs recorded before sending for signature existed.

    ``content_type`` + ``object_id`` form a generic link to the delegated document: a lab,
    imaging or referral report, or an uncategorized clinical document.
    """

    class Meta:
        db_table = "canvas_sdk_data_api_documentreviewdelegation_001"

    content_type = models.ForeignKey(
        "v1.ContentType", on_delete=models.DO_NOTHING, related_name="+"
    )
    object_id = models.IntegerField()

    delegated_by = models.ForeignKey("v1.Staff", on_delete=models.DO_NOTHING, related_name="+")
    delegated_to_staff = models.ForeignKey(
        "v1.Staff", on_delete=models.DO_NOTHING, related_name="+", null=True, blank=True
    )
    delegated_to_team = models.ForeignKey(
        "v1.Team", on_delete=models.DO_NOTHING, related_name="+", null=True, blank=True
    )
    on_behalf_of = models.ForeignKey("v1.Staff", on_delete=models.DO_NOTHING, related_name="+")

    signature_consent = models.BooleanField()
    comment = models.TextField()
    is_active = models.BooleanField()

    @property
    def is_route_back(self) -> bool:
        """True when this hop returned the signed document to whoever sent it."""
        return self.delegated_to_staff_id is not None and (
            self.delegated_to_staff_id == self.on_behalf_of_id
        )


class DelegatedDocumentMixin:
    """Review delegation accessors for the reviewable document models."""

    dbid: int
    _meta: Options

    @property
    def delegations(self) -> models.QuerySet[DocumentReviewDelegation]:
        """All review delegations for this document, oldest first."""
        return DocumentReviewDelegation.objects.filter(
            content_type__app_label="api",
            content_type__model=self._meta.model_name,
            object_id=self.dbid,
        ).order_by("created")

    @property
    def active_delegation(self) -> DocumentReviewDelegation | None:
        """The active delegation, or None when no delegation is in effect."""
        return self.delegations.filter(is_active=True).first()


__exports__ = ("DocumentReviewDelegation",)
