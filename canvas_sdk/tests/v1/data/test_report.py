import datetime

import factory
import pytest

from canvas_sdk.test_utils.factories import (
    CanvasUserFactory,
    ImagingReportFactory,
    LabReportFactory,
    PatientAdministrativeDocumentFactory,
    ReferralReportFactory,
    TeamFactory,
    UncategorizedClinicalDocumentFactory,
)
from canvas_sdk.v1.data import ReferralReport, Report, Team, UncategorizedClinicalDocument

REPORT_FACTORIES = [
    LabReportFactory,
    ImagingReportFactory,
    ReferralReportFactory,
    UncategorizedClinicalDocumentFactory,
    PatientAdministrativeDocumentFactory,
]


@pytest.mark.django_db
@pytest.mark.parametrize("report_factory", REPORT_FACTORIES)
def test_every_report_type_exposes_the_team_assignment(
    report_factory: type[factory.django.DjangoModelFactory],
) -> None:
    """Every report type is a Report and reads its team, team assignment date and assigner."""
    team = TeamFactory.create()
    assigner = CanvasUserFactory.create()
    assigned_at = datetime.datetime(2026, 10, 1, 12, 0, tzinfo=datetime.UTC)
    report = report_factory.create(
        team=team,
        team_assigned_date=assigned_at,
        assigned_by=assigner,
    )

    report.refresh_from_db()

    assert isinstance(report, Report)
    assert report.team == team
    assert report.team_assigned_date == assigned_at
    assert report.assigned_by == assigner


@pytest.mark.django_db
@pytest.mark.parametrize("report_factory", REPORT_FACTORIES)
def test_reports_can_be_filtered_by_assigned_team(
    report_factory: type[factory.django.DjangoModelFactory],
) -> None:
    """Filtering on team__id returns only the reports assigned to that team."""
    team = TeamFactory.create()
    assigned = report_factory.create(team=team)
    report_factory.create()

    model = report_factory._meta.model
    assert list(model.objects.filter(team__id=team.id)) == [assigned]


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("report_factory", "query_name", "accessor"),
    [
        (ReferralReportFactory, "referralreport", "referralreport_set"),
        (
            UncategorizedClinicalDocumentFactory,
            "uncategorizedclinicaldocument",
            "uncategorizedclinicaldocument_set",
        ),
    ],
)
def test_team_reverse_lookups_keep_their_names(
    report_factory: type[factory.django.DjangoModelFactory],
    query_name: str,
    accessor: str,
) -> None:
    """The reverse lookups from Team keep the names they had before the shared base class."""
    team = TeamFactory.create()
    report: ReferralReport | UncategorizedClinicalDocument = report_factory.create(team=team)

    assert list(Team.objects.filter(**{f"{query_name}__dbid": report.dbid})) == [team]
    assert list(getattr(team, accessor).all()) == [report]
