import pytest

from canvas_sdk.test_utils.factories import (
    DiagnosticReportCategoryCodingFactory,
    DiagnosticReportCodeCodingFactory,
    DiagnosticReportFactory,
    LabReportFactory,
)
from canvas_sdk.v1.data.diagnostic_report import (
    DiagnosticReport,
    DiagnosticReportCategoryCoding,
    DiagnosticReportCodeCoding,
    DiagnosticReportStatus,
)


@pytest.mark.django_db
def test_lab_report_diagnostic_reports_reverse_relation() -> None:
    """LabReport.diagnostic_reports returns only DiagnosticReports linked via the lab FK."""
    report = LabReportFactory.create()
    linked = DiagnosticReportFactory.create(subject=report.patient, lab=report)
    DiagnosticReportFactory.create(subject=report.patient, lab=None)

    assert [r.id for r in report.diagnostic_reports.all()] == [linked.id]


@pytest.mark.django_db
def test_diagnostic_report_resolves_to_linked_lab_report() -> None:
    """A DiagnosticReport fetched by id exposes its linked LabReport."""
    report = LabReportFactory.create()
    diagnostic_report = DiagnosticReportFactory.create(
        subject=report.patient, lab=report, status=DiagnosticReportStatus.FINAL
    )

    fetched = DiagnosticReport.objects.get(id=diagnostic_report.id)

    assert fetched.lab_id == report.dbid
    assert fetched.lab is not None
    assert fetched.lab.id == report.id
    assert fetched.status == DiagnosticReportStatus.FINAL


@pytest.mark.django_db
def test_diagnostic_report_for_patient_filters_by_subject() -> None:
    """DiagnosticReport.objects.for_patient filters by subject patient id."""
    report = LabReportFactory.create()
    matching = DiagnosticReportFactory.create(subject=report.patient, lab=report)
    DiagnosticReportFactory.create(lab=None)

    assert report.patient is not None
    results = list(DiagnosticReport.objects.for_patient(report.patient.id))

    assert [r.id for r in results] == [matching.id]


@pytest.mark.django_db
def test_diagnostic_report_category_codings_return_only_its_codings() -> None:
    """DiagnosticReport.category_codings returns only that report's codings."""
    parent = DiagnosticReportFactory.create()
    coding = DiagnosticReportCategoryCodingFactory.create(diagnostic_report=parent)
    DiagnosticReportCategoryCodingFactory.create()

    assert list(parent.category_codings.all()) == [coding]


@pytest.mark.django_db
def test_diagnostic_report_category_coding_resolves_to_its_diagnostic_report() -> None:
    """The diagnostic_report foreign key resolves to the parent DiagnosticReport."""
    parent = DiagnosticReportFactory.create()
    coding = DiagnosticReportCategoryCodingFactory.create(diagnostic_report=parent)

    fetched = DiagnosticReportCategoryCoding.objects.get(dbid=coding.dbid)

    assert fetched.diagnostic_report == parent


@pytest.mark.django_db
def test_diagnostic_report_codings_return_only_its_codings() -> None:
    """DiagnosticReport.codings returns only that report's codings."""
    parent = DiagnosticReportFactory.create()
    coding = DiagnosticReportCodeCodingFactory.create(diagnostic_report=parent)
    DiagnosticReportCodeCodingFactory.create()

    assert list(parent.codings.all()) == [coding]


@pytest.mark.django_db
def test_diagnostic_report_code_coding_resolves_to_its_diagnostic_report() -> None:
    """The diagnostic_report foreign key resolves to the parent DiagnosticReport."""
    parent = DiagnosticReportFactory.create()
    coding = DiagnosticReportCodeCodingFactory.create(diagnostic_report=parent)

    fetched = DiagnosticReportCodeCoding.objects.get(dbid=coding.dbid)

    assert fetched.diagnostic_report == parent
