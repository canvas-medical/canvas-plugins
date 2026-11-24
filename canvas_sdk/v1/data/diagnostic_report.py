from django.db import models

from canvas_sdk.v1.data.base import (
    BaseQuerySet,
    ForPatientQuerySetMixin,
    IdentifiableModel,
    TimestampedModel,
)
from canvas_sdk.v1.data.coding import Coding


class DiagnosticReportStatus(models.TextChoices):
    """Status choices for DiagnosticReport."""

    REGISTERED = "registered", "Registered"
    PARTIAL = "partial", "Partial"
    PRELIMINARY = "preliminary", "Preliminary"
    FINAL = "final", "Final"
    AMENDED = "amended", "Amended"
    CORRECTED = "corrected", "Corrected"
    APPENDED = "appended", "Appended"
    CANCELLED = "cancelled", "Cancelled"
    ENTERED_IN_ERROR = "entered-in-error", "Entered-in-error"
    UNKNOWN = "unknown", "Unknown"


class DiagnosticReportQuerySet(ForPatientQuerySetMixin, BaseQuerySet):
    """QuerySet for DiagnosticReport."""

    def for_patient(self, patient_id: str) -> "DiagnosticReportQuerySet":
        """Return a queryset filtered by patient via the subject relationship."""
        return self.filter(subject__id=patient_id)


class DiagnosticReport(TimestampedModel, IdentifiableModel):
    """The FHIR DiagnosticReport linked to a LabReport in the Canvas data module."""

    class Meta:
        db_table = "canvas_sdk_data_api_diagnosticreport_001"

    objects = DiagnosticReportQuerySet.as_manager()

    status = models.CharField(
        choices=DiagnosticReportStatus.choices,
        max_length=20,
        default=DiagnosticReportStatus.UNKNOWN,
    )
    subject = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="diagnostic_reports"
    )
    lab = models.ForeignKey(
        "v1.LabReport",
        on_delete=models.DO_NOTHING,
        related_name="diagnostic_reports",
        null=True,
    )


class DiagnosticReportCategoryCoding(Coding):
    """A category coding on a diagnostic report."""

    class Meta:
        db_table = "canvas_sdk_data_api_diagnosticreportcategorycoding_001"

    diagnostic_report = models.ForeignKey(
        DiagnosticReport, on_delete=models.DO_NOTHING, related_name="category_codings"
    )


class DiagnosticReportCodeCoding(Coding):
    """A code coding on a diagnostic report."""

    class Meta:
        db_table = "canvas_sdk_data_api_diagnosticreportcodecoding_001"

    diagnostic_report = models.ForeignKey(
        DiagnosticReport, on_delete=models.DO_NOTHING, related_name="codings"
    )


__exports__ = (
    "DiagnosticReport",
    "DiagnosticReportCategoryCoding",
    "DiagnosticReportCodeCoding",
    "DiagnosticReportStatus",
)
