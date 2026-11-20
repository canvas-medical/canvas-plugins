from django.db import models

from canvas_sdk.v1.data.base import Model, TimestampedModel


class SuspectHCCStatus(models.TextChoices):
    """Whether a suspected HCC is still open on the patient."""

    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"


class SuspectHCCKind(models.TextChoices):
    """Why an HCC is suspected."""

    IMPLIED_BY_CLINICAL_DATA = "implied_by_clinical_data", "Implied by Clinical Data"
    PREVIOUS_CONDITION = "previous_condition", "Previous Condition"
    UNKNOWN = "unknown", "Unknown"


class SuspectHCC(TimestampedModel):
    """A Hierarchical Condition Category suspected on a patient."""

    class Meta:
        db_table = "canvas_sdk_data_api_suspecthcc_001"

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="suspect_hccs"
    )
    status = models.CharField(max_length=20, choices=SuspectHCCStatus.choices)
    hcc_description = models.TextField()
    hcc_code = models.TextField()
    reasons = models.JSONField(default=list)
    previous_condition = models.TextField()
    kind = models.CharField(max_length=50, choices=SuspectHCCKind.choices)


class Campaign(Model):
    """An outreach campaign built on a protocol."""

    class Meta:
        db_table = "canvas_sdk_data_api_campaign_001"

    title = models.CharField(max_length=255)
    description = models.CharField(max_length=512, null=True)
    closed_at = models.DateTimeField(null=True)
    # api_protocolused is not exposed to plugins, so the protocol is a plain id.
    protocol_id = models.IntegerField()
    work_list = models.BooleanField()
    total_patients_on_closure = models.IntegerField()
    satisfied_patients_on_closure = models.IntegerField()


class Intervention(TimestampedModel):
    """One outreach step of a campaign, sent to its patients with a letter template."""

    class Meta:
        db_table = "canvas_sdk_data_api_intervention_001"

    campaign = models.ForeignKey(
        "v1.Campaign", on_delete=models.DO_NOTHING, related_name="interventions"
    )
    patients = models.ManyToManyField(
        "v1.Patient", through="v1.InterventionPatient", related_name="interventions"
    )
    template = models.ForeignKey(
        "v1.LetterTemplate", on_delete=models.DO_NOTHING, related_name="interventions"
    )
    start_delivery = models.DateTimeField()
    author = models.ForeignKey(
        "v1.Staff", on_delete=models.DO_NOTHING, related_name="interventions"
    )


class InterventionPatient(Model):
    """A patient targeted by an intervention."""

    class Meta:
        db_table = "canvas_sdk_data_api_intervention_patients_001"

    intervention = models.ForeignKey(
        "v1.Intervention", on_delete=models.DO_NOTHING, related_name="+"
    )
    patient = models.ForeignKey("v1.Patient", on_delete=models.DO_NOTHING, related_name="+")


__exports__ = (
    "Campaign",
    "Intervention",
    "InterventionPatient",
    "SuspectHCC",
    "SuspectHCCKind",
    "SuspectHCCStatus",
)
