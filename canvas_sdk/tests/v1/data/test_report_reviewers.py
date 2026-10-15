import factory
import pytest

from canvas_sdk.test_utils.factories import (
    ImagingReportFactory,
    LabReportFactory,
    PatientAdministrativeDocumentFactory,
    ReferralReportFactory,
    StaffFactory,
    UncategorizedClinicalDocumentFactory,
)

REPORT_FACTORIES = [
    LabReportFactory,
    ImagingReportFactory,
    ReferralReportFactory,
    UncategorizedClinicalDocumentFactory,
    PatientAdministrativeDocumentFactory,
]


@pytest.mark.django_db
@pytest.mark.parametrize("report_factory", REPORT_FACTORIES)
def test_reviewers_returns_the_staff_assigned_to_review_the_report(
    report_factory: type[factory.django.DjangoModelFactory],
) -> None:
    """A report exposes the staff assigned to review it via the reviewers relation."""
    report = report_factory.create()
    reviewer = StaffFactory.create()
    other_reviewer = StaffFactory.create()
    report.reviewers.add(reviewer, other_reviewer)

    assert set(report.reviewers.values_list("id", flat=True)) == {
        reviewer.id,
        other_reviewer.id,
    }


@pytest.mark.django_db
@pytest.mark.parametrize("report_factory", REPORT_FACTORIES)
def test_reports_can_be_filtered_by_assigned_reviewer(
    report_factory: type[factory.django.DjangoModelFactory],
) -> None:
    """Filtering on reviewers__id returns only the reports assigned to that staff member."""
    reviewer = StaffFactory.create()
    assigned = report_factory.create()
    report_factory.create()
    assigned.reviewers.add(reviewer)

    model = report_factory._meta.model
    assert list(model.objects.filter(reviewers__id=reviewer.id)) == [assigned]


@pytest.mark.django_db
@pytest.mark.parametrize("report_factory", REPORT_FACTORIES)
def test_reviewers_is_empty_when_unassigned(
    report_factory: type[factory.django.DjangoModelFactory],
) -> None:
    """A report with no assigned reviewers returns an empty reviewers relation."""
    report = report_factory.create()

    assert not report.reviewers.exists()
