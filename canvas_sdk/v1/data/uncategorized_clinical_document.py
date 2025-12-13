from typing import cast

from django.db import models

from canvas_sdk.v1.data.base import (
    AuditedModel,
    BaseModelManager,
    BaseQuerySet,
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
    IdentifiableModel,
    TimestampedModel,
)


class UncategorizedClinicalDocumentReviewQuerySet(
    CommittableQuerySetMixin, ForPatientQuerySetMixin, BaseQuerySet
):
    """A queryset for uncategorized clinical document reviews."""

    pass


UncategorizedClinicalDocumentReviewManager = BaseModelManager.from_queryset(
    UncategorizedClinicalDocumentReviewQuerySet
)


class UncategorizedClinicalDocumentReview(AuditedModel, IdentifiableModel):
    """UncategorizedClinicalDocumentReview."""

    class Meta:
        db_table = "canvas_sdk_data_api_uncategorizeddocumentreview_001"

    objects = cast(
        UncategorizedClinicalDocumentReviewQuerySet, UncategorizedClinicalDocumentReviewManager()
    )

    internal_comment = models.TextField()
    message_to_patient = models.CharField(max_length=2048)
    status = models.CharField(max_length=50)
    patient = models.ForeignKey(
        "v1.Patient",
        on_delete=models.DO_NOTHING,
        related_name="uncategorized_clinical_document_reviews",
        null=True,
    )
    patient_communication_method = models.CharField(max_length=30)


class UncategorizedClinicalDocument(TimestampedModel, IdentifiableModel):
    """UncategorizedClinicalDocument."""

    class Meta:
        db_table = "canvas_sdk_data_api_uncategorizedclinicaldocument_001"

    patient = models.ForeignKey("v1.Patient", on_delete=models.DO_NOTHING, related_name="+")
    originator = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    assigned_by = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    review = models.ForeignKey(
        "v1.UncategorizedClinicalDocumentReview",
        related_name="reports",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    team = models.ForeignKey("v1.Team", on_delete=models.DO_NOTHING, null=True)

    name = models.CharField(max_length=255)
    review_mode = models.CharField(max_length=2)
    junked = models.BooleanField(default=False)
    requires_signature = models.BooleanField(default=False)
    assigned_date = models.DateTimeField(null=True)
    team_assigned_date = models.DateTimeField(null=True)
    original_date = models.DateField(null=True)
    comment = models.TextField(default="", blank=True)
    priority = models.BooleanField(default=False)


__exports__ = ("UncategorizedClinicalDocumentReview", "UncategorizedClinicalDocument")
