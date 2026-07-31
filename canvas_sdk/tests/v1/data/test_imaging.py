import pytest

from canvas_sdk.test_utils.factories import (
    ImagingReportCodingFactory,
    ImagingReportFactory,
)
from canvas_sdk.v1.data.imaging import ImagingReport
from canvas_sdk.value_set.value_set import ValueSet


class _ColonoscopyValueSet(ValueSet):
    """Tiny value set fixture for find() tests."""

    VALUE_SET_NAME = "Colonoscopy Sample"
    OID = "tests.colonoscopy-sample"
    CPT = {"44388", "45378"}


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


@pytest.mark.django_db
def test_find_returns_reports_with_codings_in_value_set() -> None:
    """ImagingReport.objects.find(value_set) matches via codings__system/code."""
    matching = ImagingReportFactory.create()
    ImagingReportCodingFactory.create(
        report=matching, system="http://www.ama-assn.org/go/cpt", code="44388"
    )
    other = ImagingReportFactory.create()
    ImagingReportCodingFactory.create(
        report=other, system="http://www.ama-assn.org/go/cpt", code="99999"
    )

    found = list(ImagingReport.objects.find(_ColonoscopyValueSet))

    assert [r.id for r in found] == [matching.id]


@pytest.mark.django_db
def test_find_excludes_codings_with_wrong_system() -> None:
    """A code matching the CPT set under a different code system is not returned."""
    report = ImagingReportFactory.create()
    ImagingReportCodingFactory.create(report=report, system="http://snomed.info/sct", code="44388")

    assert list(ImagingReport.objects.find(_ColonoscopyValueSet)) == []
