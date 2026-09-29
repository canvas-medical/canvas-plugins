from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel


class DocumentReviewDelegation(TimestampedModel, IdentifiableModel):
    """A signature release written when a reviewable document is reassigned.

    Append-only log with a single active row per document (``is_active``). ``on_behalf_of``
    is the staff member who released their signature; with ``signature_consent`` set, the
    recipients (a staff member, a team, or both) may apply that signature while annotating.
    A later plain reassign deactivates the row, so a release reaches only its direct
    recipients.

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
