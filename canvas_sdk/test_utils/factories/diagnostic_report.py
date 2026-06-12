import factory

from canvas_sdk.v1.data import DiagnosticReport
from canvas_sdk.v1.data.diagnostic_report import DiagnosticReportStatus


class DiagnosticReportFactory(factory.django.DjangoModelFactory[DiagnosticReport]):
    """Factory for creating a DiagnosticReport."""

    class Meta:
        model = DiagnosticReport

    status = DiagnosticReportStatus.FINAL
    subject = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    lab = None
