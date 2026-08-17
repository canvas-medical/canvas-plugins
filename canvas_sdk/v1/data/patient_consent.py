from typing import TYPE_CHECKING

from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel
from canvas_sdk.v1.data.coding import Coding
from canvas_sdk.v1.data.utils import presigned_url

if TYPE_CHECKING:
    from canvas_sdk.v1.data.document_reference import DocumentReference
    from canvas_sdk.v1.data.patient_administrative_document import PatientAdministrativeDocument


class PatientConsentRejectionCoding(Coding):
    """Patient Consent Rejection Coding."""

    class Meta:
        db_table = "canvas_sdk_data_api_patientconsentrejectioncoding_001"


class PatientConsentExpirationRule(models.TextChoices):
    """PatientConsentExpirationRule."""

    NEVER = "never", "Never"
    IN_ONE_YEAR = "in_one_year", "In one year"
    END_OF_YEAR = "end_of_year", "End of year"


class PatientConsentCoding(Coding):
    """Patient Consent Coding."""

    class Meta:
        db_table = "canvas_sdk_data_api_patientconsentcoding_001"

    expiration_rule = models.CharField(choices=PatientConsentExpirationRule.choices, max_length=255)
    is_mandatory = models.BooleanField()
    is_proof_required = models.BooleanField()
    show_in_patient_portal = models.BooleanField()
    summary = models.TextField()
    document = models.FileField(null=True)

    @property
    def document_url(self) -> str | None:
        """Return a presigned URL for accessing the consent document.

        Returns the presigned S3 URL if a document file exists,
        otherwise returns None.
        """
        if self.document:
            return presigned_url(self.document.name)
        return None


class PatientConsentStatus(models.TextChoices):
    """PatientConsentStatus."""

    ACCEPTED = "accepted", "Accepted"
    ACCEPTED_VIA_PORTAL = (
        "accepted_via_patient_portal",
        "Accepted Via Patient Portal",
    )
    REJECTED = "rejected", "Rejected"
    REJECTED_VIA_PORTAL = "rejected_via_patient_portal", "Rejected Via Patient Portal"


class PatientConsent(IdentifiableModel):
    """Patient Consent."""

    class Meta:
        db_table = "canvas_sdk_data_api_patientconsent_001"

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="patient_consent"
    )
    category = models.ForeignKey(
        "v1.PatientConsentCoding",
        on_delete=models.DO_NOTHING,
        related_name="patient_consent",
    )
    state = models.CharField(choices=PatientConsentStatus, max_length=255)
    effective_date = models.DateField()
    expired_date = models.DateField()
    rejection_reason = models.ForeignKey(
        "v1.PatientConsentRejectionCoding",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="patient_consents",
    )
    originator = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, related_name="+")
    documents = models.ManyToManyField(
        "v1.PatientAdministrativeDocument",
        related_name="patient_consents",
        db_table="canvas_sdk_data_api_patientconsent_documents_001",
        blank=True,
    )

    @property
    def active_document(self) -> "PatientAdministrativeDocument | None":
        """The current signed consent document: the latest non-junked document by original date."""
        documents = self.documents.filter(junked=False)
        dated = documents.filter(original_date__isnull=False)
        if dated.exists():
            return dated.order_by("original_date", "modified").last()
        return documents.order_by("dbid").last()

    @property
    def document_references(self) -> "models.QuerySet[DocumentReference]":
        """The DocumentReferences for this consent's signed documents."""
        from canvas_sdk.v1.data.document_reference import DocumentReference

        return DocumentReference.objects.filter(
            content_type__app_label="api",
            content_type__model="patientadministrativedocument",
            object_id__in=self.documents.values_list("dbid", flat=True),
        )


__exports__ = (
    "PatientConsent",
    "PatientConsentCoding",
    "PatientConsentRejectionCoding",
)
