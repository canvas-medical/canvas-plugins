import pytest

from canvas_sdk.test_utils.factories import (
    ImagingReportCodingFactory,
    ImagingReportFactory,
)


@pytest.mark.django_db
def test_codings_returns_only_codings_for_the_report() -> None:
    """Test the codings reverse accessor returns only codings linked to the report."""
    report = ImagingReportFactory.create()
    coding = ImagingReportCodingFactory.create(report=report)
    ImagingReportCodingFactory.create(report=ImagingReportFactory.create())

    codings = list(report.codings.all())

    assert [c.dbid for c in codings] == [coding.dbid]


@pytest.mark.django_db
def test_coding_fields_are_persisted() -> None:
    """Test an imaging report coding's fields round-trip through the database."""
    report = ImagingReportFactory.create()
    ImagingReportCodingFactory.create(
        report=report,
        system="http://loinc.org",
        code="24590-2",
        display="US Retroperitoneum",
        value="positive",
    )

    fetched = report.codings.get()

    assert fetched.system == "http://loinc.org"
    assert fetched.code == "24590-2"
    assert fetched.display == "US Retroperitoneum"
    assert fetched.value == "positive"
