from typing import TypeAlias

from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel
from canvas_sdk.v1.data.django_content_type import resolve_content_object
from canvas_sdk.v1.data.imaging import ImagingReport
from canvas_sdk.v1.data.lab import LabReport
from canvas_sdk.v1.data.patient_administrative_document import PatientAdministrativeDocument
from canvas_sdk.v1.data.referral import ReferralReport
from canvas_sdk.v1.data.uncategorized_clinical_document import UncategorizedClinicalDocument
from canvas_sdk.v1.data.utils import presigned_url

AnnotatedDocument: TypeAlias = (
    LabReport
    | ImagingReport
    | ReferralReport
    | PatientAdministrativeDocument
    | UncategorizedClinicalDocument
)

# The SDK model for each content type an annotation links to, keyed by (app_label, model).
_ANNOTATED_DOCUMENT_MODELS: dict[tuple[str, str], type[AnnotatedDocument]] = {
    ("api", "labreport"): LabReport,
    ("api", "imagingreport"): ImagingReport,
    ("api", "referralreport"): ReferralReport,
    ("api", "patientadministrativedocument"): PatientAdministrativeDocument,
    ("api", "uncategorizedclinicaldocument"): UncategorizedClinicalDocument,
}


class DocumentAnnotation(TimestampedModel, IdentifiableModel):
    """An annotated version of a document, saved each time staff annotate or sign it.

    ``content_type`` + ``object_id`` link the annotation to its lab, imaging or referral report,
    or administrative or uncategorized clinical document. An annotation made before the document
    was filed links to its ``integration_task`` instead.
    """

    class Meta:
        db_table = "canvas_sdk_data_api_documentannotation_001"

    document = models.FileField()
    created_by = models.ForeignKey(
        "v1.Staff", on_delete=models.DO_NOTHING, related_name="document_annotations"
    )
    signers = models.ManyToManyField(
        "v1.Staff",
        related_name="signed_document_annotations",
        db_table="canvas_sdk_data_api_documentannotation_signers_001",
        blank=True,
    )
    has_signature_spot = models.BooleanField(default=False)
    integration_task = models.ForeignKey(
        "v1.IntegrationTask",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_annotations",
    )
    content_type = models.ForeignKey(
        "v1.ContentType", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    object_id = models.IntegerField(null=True)

    @property
    def document_url(self) -> str | None:
        """Return a presigned URL for the annotated PDF, or None if unset."""
        if self.document:
            return presigned_url(self.document.name)
        return None

    @property
    def related_object(self) -> AnnotatedDocument | None:
        """The report or document this annotation was made on, else None."""
        return resolve_content_object(_ANNOTATED_DOCUMENT_MODELS, self.content_type, self.object_id)


__exports__ = ("DocumentAnnotation",)
