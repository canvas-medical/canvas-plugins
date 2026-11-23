from typing import TypeAlias

from django.db import models

from canvas_sdk.v1.data.base import TimestampedModel
from canvas_sdk.v1.data.coverage import Coverage
from canvas_sdk.v1.data.django_content_type import resolve_content_object
from canvas_sdk.v1.data.imaging import ImagingReport
from canvas_sdk.v1.data.lab import LabReport
from canvas_sdk.v1.data.note import Note
from canvas_sdk.v1.data.patient import PatientIdentificationCard
from canvas_sdk.v1.data.patient_administrative_document import PatientAdministrativeDocument
from canvas_sdk.v1.data.referral import ReferralReport
from canvas_sdk.v1.data.uncategorized_clinical_document import UncategorizedClinicalDocument


class PatientChartDocument(TimestampedModel):
    """A chart page that can be printed and attached to a letter.

    ``url`` is a path template with a ``{key}`` placeholder for the patient's id.
    """

    class Meta:
        db_table = "canvas_sdk_data_api_patientchartdocument_001"

    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)


LetterAttachment: TypeAlias = (
    LabReport
    | ImagingReport
    | ReferralReport
    | PatientAdministrativeDocument
    | UncategorizedClinicalDocument
    | Note
    | PatientChartDocument
    | Coverage
    | PatientIdentificationCard
)

# The SDK model for each content type a letter document links to, keyed by (app_label, model).
_LETTER_ATTACHMENT_MODELS: dict[tuple[str, str], type[LetterAttachment]] = {
    ("api", "labreport"): LabReport,
    ("api", "imagingreport"): ImagingReport,
    ("api", "referralreport"): ReferralReport,
    ("api", "patientadministrativedocument"): PatientAdministrativeDocument,
    ("api", "uncategorizedclinicaldocument"): UncategorizedClinicalDocument,
    ("api", "note"): Note,
    ("api", "patientchartdocument"): PatientChartDocument,
    ("api", "coverage"): Coverage,
    ("api", "patientidentificationcard"): PatientIdentificationCard,
}


class LetterDocument(TimestampedModel):
    """A document attached to a letter; ``content_type`` + ``object_id`` link to it."""

    class Meta:
        db_table = "canvas_sdk_data_api_letterdocument_001"

    letter = models.ForeignKey("v1.Letter", on_delete=models.DO_NOTHING, related_name="documents")
    label = models.CharField(max_length=500)
    category = models.CharField(max_length=500, default="")
    content_type = models.ForeignKey(
        "v1.ContentType", on_delete=models.DO_NOTHING, related_name="+"
    )
    object_id = models.IntegerField()

    @property
    def related_object(self) -> LetterAttachment | None:
        """The report, document, note, chart page, coverage or ID card attached, else None."""
        return resolve_content_object(_LETTER_ATTACHMENT_MODELS, self.content_type, self.object_id)


class ReferralDocument(TimestampedModel):
    """A document attached to a referral.

    ``document_type`` + ``document_id`` name the attached document; ``url`` + ``bucket`` hold the
    S3 location of an uploaded file.
    """

    class Meta:
        db_table = "canvas_sdk_data_api_referraldocument_001"

    referral = models.ForeignKey(
        "v1.Referral", on_delete=models.DO_NOTHING, related_name="documents"
    )
    url = models.CharField(max_length=1000, null=True, blank=True)
    bucket = models.CharField(max_length=500, null=True, blank=True)
    document_type = models.CharField(max_length=250)
    label = models.CharField(max_length=500)
    document_id = models.IntegerField(null=True)


__exports__ = ("LetterDocument", "PatientChartDocument", "ReferralDocument")
