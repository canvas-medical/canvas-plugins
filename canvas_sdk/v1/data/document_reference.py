from django.db import models

from canvas_sdk.v1.data.base import (
    BaseQuerySet,
    ForPatientQuerySetMixin,
    IdentifiableModel,
    TimestampedModel,
)
from canvas_sdk.v1.data.coding import Coding
from canvas_sdk.v1.data.utils import presigned_url


class DocumentReferenceStatus(models.TextChoices):
    """Status choices for DocumentReference."""

    CURRENT = "current", "Current"
    SUPERSEDED = "superseded", "Superseded"
    ENTERED_IN_ERROR = "entered-in-error", "Entered in Error"


class DocumentReferenceCoding(Coding):
    """DocumentReferenceCoding."""

    class Meta:
        db_table = "canvas_sdk_data_api_documentreferencecoding_001"


class DocumentReferenceCategory(Coding):
    """DocumentReferenceCategory."""

    class Meta:
        db_table = "canvas_sdk_data_api_documentreferencecategory_001"


class DocumentReferenceQuerySet(ForPatientQuerySetMixin, BaseQuerySet):
    """QuerySet for DocumentReference."""

    def for_patient(self, patient_id: str) -> "DocumentReferenceQuerySet":
        """Return a queryset filtered by patient via subject relationship."""
        return self.filter(subject__patient__id=patient_id)


class DocumentReference(TimestampedModel, IdentifiableModel):
    """DocumentReference model for storing references to documents."""

    class Meta:
        db_table = "canvas_sdk_data_api_documentreference_001"

    objects = DocumentReferenceQuerySet.as_manager()

    document = models.CharField(max_length=255, null=True, blank=True)
    document_absolute_url = models.URLField(max_length=512, null=True, blank=True)
    document_content_type = models.CharField(max_length=512)
    business_identifier = models.CharField(max_length=36, default="")

    originator = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, related_name="+", null=True
    )
    subject = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, related_name="+", null=True
    )
    type = models.ForeignKey(
        DocumentReferenceCoding,
        related_name="document_references",
        on_delete=models.DO_NOTHING,
    )
    category = models.ForeignKey(
        DocumentReferenceCategory,
        related_name="document_references",
        on_delete=models.DO_NOTHING,
        null=True,
    )

    status = models.CharField(
        choices=DocumentReferenceStatus.choices,
        default=DocumentReferenceStatus.CURRENT,
        max_length=16,
    )

    date = models.DateField()

    encounter = models.ForeignKey(
        "v1.Encounter", on_delete=models.DO_NOTHING, null=True, related_name="document_references"
    )
    team = models.ForeignKey(
        "v1.Team",
        related_name="document_references",
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
    )

    related_object_document_title = models.CharField(max_length=255, null=True, blank=True)
    related_object_document_comment = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self) -> str:
        return f"DocumentReference(id={self.id})"

    @property
    def document_url(self) -> str | None:
        """
        Return a presigned URL for accessing the document.

        Returns the presigned S3 URL if a document file exists,
        otherwise returns the absolute URL if set.
        """
        if self.document:
            return presigned_url(self.document)
        return self.document_absolute_url


__exports__ = (
    "DocumentReferenceStatus",
    "DocumentReferenceCoding",
    "DocumentReferenceCategory",
    "DocumentReference",
)
