from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel


class DocumentReviewDelegation(TimestampedModel, IdentifiableModel):
    """A hand-off of a reviewable document from one staff member (or team) to another.

    Append-only log with a single active row per document (``is_active``). Delegation is
    A<->B only: an owner delegates the document out, and the recipient may only route it
    back. ``on_behalf_of`` identifies the original owner and, when ``signature_consent`` is
    set, the staff member whose signature the recipient may apply while annotating.

    ``content_type`` + ``object_id`` form a generic link to the delegated document (e.g. an
    UncategorizedClinicalDocument).
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
        """True when this hop returned the document to its original owner."""
        return self.delegated_to_staff_id is not None and (
            self.delegated_to_staff_id == self.on_behalf_of_id
        )


__exports__ = ("DocumentReviewDelegation",)
