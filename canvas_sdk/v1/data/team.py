from django.contrib.postgres.fields import ArrayField
from django.db import models

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


class Team(models.Model):
    """Team."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_team_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    name = models.CharField()
    responsibilities = ArrayField(models.CharField(choices=TeamResponsibility.choices))
    members = models.ManyToManyField(  # type: ignore[var-annotated]
        "v1.Staff",
        related_name="teams",
        db_table="canvas_sdk_data_api_team_members_001",
    )


class TeamContactPoint(models.Model):
    """TeamContactPoint."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_teamcontactpoint_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    system = models.CharField(choices=ContactPointSystem.choices)
    value = models.CharField()
    use = models.CharField(choices=ContactPointUse.choices)
    use_notes = models.CharField()
    rank = models.IntegerField()
    state = models.CharField(choices=ContactPointState.choices)
    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING, related_name="telecom")


__exports__ = (
    "TeamResponsibility",
    "Team",
    "TeamContactPoint",
)
