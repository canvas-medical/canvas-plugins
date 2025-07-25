from django.contrib.postgres.fields import ArrayField
from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel
from canvas_sdk.v1.data.common import ContactPointState, ContactPointSystem, ContactPointUse


class TeamResponsibility(models.TextChoices):
    """TeamResponsibility."""

    COLLECT_SPECIMENS_FROM_PATIENT = (
        "COLLECT_SPECIMENS_FROM_PATIENT",
        "Collect specimens from a patient",
    )
    COMMUNICATE_DIAGNOSTIC_RESULTS_TO_PATIENT = (
        "COMMUNICATE_DIAGNOSTIC_RESULTS_TO_PATIENT",
        "Communicate diagnostic results to patient",
    )
    COORDINATE_REFERRALS_FOR_PATIENT = (
        "COORDINATE_REFERRALS_FOR_PATIENT",
        "Coordinate referrals for a patient",
    )
    PROCESS_REFILL_REQUESTS = "PROCESS_REFILL_REQUESTS", "Process refill requests from a pharmacy"
    PROCESS_CHANGE_REQUESTS = "PROCESS_CHANGE_REQUESTS", "Process change requests from a pharmacy"
    SCHEDULE_LAB_VISITS_FOR_PATIENT = (
        "SCHEDULE_LAB_VISITS_FOR_PATIENT",
        "Schedule lab visits for a patient",
    )
    POPULATION_HEALTH_CAMPAIGN_OUTREACH = (
        "POPULATION_HEALTH_CAMPAIGN_OUTREACH",
        "Population health campaign outreach",
    )
    COLLECT_PATIENT_PAYMENTS = "COLLECT_PATIENT_PAYMENTS", "Collect patient payments"
    COMPLETE_OPEN_LAB_ORDERS = "COMPLETE_OPEN_LAB_ORDERS", "Complete open lab orders"
    REVIEW_ERA_POSTING_EXCEPTIONS = (
        "REVIEW_ERA_POSTING_EXCEPTIONS",
        "Review electronic remittance posting exceptions",
    )
    REVIEW_COVERAGES = "REVIEW_COVERAGES", "Review incomplete patient coverages"


class Team(IdentifiableModel):
    """Team."""

    class Meta:
        db_table = "canvas_sdk_data_api_team_001"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=200)
    responsibilities = ArrayField(
        models.CharField(choices=TeamResponsibility.choices, max_length=64)
    )
    members = models.ManyToManyField(
        "v1.Staff",
        related_name="teams",
        db_table="canvas_sdk_data_api_team_members_001",
    )


class TeamContactPoint(IdentifiableModel):
    """TeamContactPoint."""

    class Meta:
        db_table = "canvas_sdk_data_api_teamcontactpoint_001"

    system = models.CharField(choices=ContactPointSystem.choices, max_length=20)
    value = models.CharField(max_length=100)
    use = models.CharField(choices=ContactPointUse.choices, max_length=20)
    use_notes = models.CharField(max_length=255)
    rank = models.IntegerField()
    state = models.CharField(choices=ContactPointState.choices, max_length=20)
    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING, related_name="telecom")


__exports__ = (
    "TeamResponsibility",
    "Team",
    "TeamContactPoint",
)
