import factory

from canvas_sdk.v1.data import (
    DiagnosticReport,
    DiagnosticReportCategoryCoding,
    DiagnosticReportCodeCoding,
)
from canvas_sdk.v1.data.diagnostic_report import DiagnosticReportStatus


class DiagnosticReportFactory(factory.django.DjangoModelFactory[DiagnosticReport]):
    """Factory for creating a DiagnosticReport."""

    class Meta:
        model = DiagnosticReport

    status = DiagnosticReportStatus.FINAL
    subject = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    lab = None


class DiagnosticReportCategoryCodingFactory(
    factory.django.DjangoModelFactory[DiagnosticReportCategoryCoding]
):
    """Factory for creating a DiagnosticReportCategoryCoding."""

    class Meta:
        model = DiagnosticReportCategoryCoding

    diagnostic_report = factory.SubFactory(DiagnosticReportFactory)
    system = "http://terminology.hl7.org/CodeSystem/v2-0074"
    code = "LAB"
    display = "Laboratory"


class DiagnosticReportCodeCodingFactory(
    factory.django.DjangoModelFactory[DiagnosticReportCodeCoding]
):
    """Factory for creating a DiagnosticReportCodeCoding."""

    class Meta:
        model = DiagnosticReportCodeCoding

    diagnostic_report = factory.SubFactory(DiagnosticReportFactory)
    system = factory.Faker(
        "random_element", elements=["http://loinc.org", "http://snomed.info/sct"]
    )
    code = factory.Faker("bothify", text="#####-#")
    display = factory.Faker("text", max_nb_chars=200)
