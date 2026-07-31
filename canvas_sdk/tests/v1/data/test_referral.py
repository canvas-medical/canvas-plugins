import pytest

from canvas_sdk.test_utils.factories import (
    ReferralReportCodingFactory,
    ReferralReportFactory,
)
from canvas_sdk.v1.data.referral import ReferralReport
from canvas_sdk.value_set.value_set import ValueSet


class _DialysisServicesValueSet(ValueSet):
    """Tiny value set fixture for find() tests."""

    VALUE_SET_NAME = "Dialysis Services Sample"
    OID = "tests.dialysis-services-sample"
    SNOMEDCT = {"714749008", "385971003"}


@pytest.mark.django_db
def test_codings_returns_only_codings_for_the_report() -> None:
    """The codings reverse accessor returns only codings linked to the given report."""
    report = ReferralReportFactory.create()
    coding = ReferralReportCodingFactory.create(report=report)
    ReferralReportCodingFactory.create(report=ReferralReportFactory.create())

    codings = list(report.codings.all())

    assert [c.dbid for c in codings] == [coding.dbid]


@pytest.mark.django_db
def test_coding_fields_are_persisted() -> None:
    """A referral report coding's fields round-trip through the database."""
    report = ReferralReportFactory.create()
    ReferralReportCodingFactory.create(
        report=report,
        system="http://snomed.info/sct",
        code="714749008",
        display="Hemodialysis",
        value="ongoing",
    )

    fetched = report.codings.get()

    assert fetched.system == "http://snomed.info/sct"
    assert fetched.code == "714749008"
    assert fetched.display == "Hemodialysis"
    assert fetched.value == "ongoing"


@pytest.mark.django_db
def test_find_returns_reports_with_codings_in_value_set() -> None:
    """ReferralReport.objects.find(value_set) matches via codings__system/code."""
    matching = ReferralReportFactory.create()
    ReferralReportCodingFactory.create(
        report=matching, system="http://snomed.info/sct", code="714749008"
    )
    other = ReferralReportFactory.create()
    ReferralReportCodingFactory.create(report=other, system="http://snomed.info/sct", code="99999")

    found = list(ReferralReport.objects.find(_DialysisServicesValueSet))

    assert [r.id for r in found] == [matching.id]


@pytest.mark.django_db
def test_find_excludes_codings_with_wrong_system() -> None:
    """A code matching the SNOMED set under a different code system is not returned."""
    report = ReferralReportFactory.create()
    ReferralReportCodingFactory.create(report=report, system="http://loinc.org", code="714749008")

    assert list(ReferralReport.objects.find(_DialysisServicesValueSet)) == []
