from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel


class PatientGroup(IdentifiableModel):
    """A collection of patients."""

    class Meta:
        db_table = "canvas_sdk_data_api_patientgroup_001"

    name = models.CharField(max_length=200)

    def __str__(self) -> str:
        return self.name


class PatientGroupMembership(TimestampedModel):
    """A patient's membership in a group."""

    class Meta:
        db_table = "canvas_sdk_data_api_patientgroupmember_001"

    patient_group = models.ForeignKey(
        PatientGroup, on_delete=models.DO_NOTHING, related_name="memberships"
    )
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="patient_group_memberships"
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True)
    locked = models.BooleanField()

    def __str__(self) -> str:
        return f"PatientGroupMembership(patient_group={self.patient_group_id}, patient={self.patient_id})"


__exports__ = (
    "PatientGroup",
    "PatientGroupMembership",
)
