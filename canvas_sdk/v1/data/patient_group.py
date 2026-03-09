from django.db import models
from django.utils import timezone

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel


class PatientGroup(IdentifiableModel):
    """A collection of patients."""

    class Meta:
        db_table = "canvas_sdk_data_api_patientgroup_001"

    name = models.CharField(max_length=200, unique=True)
    members = models.ManyToManyField(
        "v1.Patient",
        through="v1.PatientGroupMember",
        default=None,
        blank=True,
        related_name="patient_groups",
    )

    def __str__(self) -> str:
        return self.name


class PatientGroupMember(TimestampedModel):
    """A patient's membership in a group."""

    class Meta:
        db_table = "canvas_sdk_data_api_patientgroupmember_001"

    patient_group = models.ForeignKey("v1.PatientGroup", models.CASCADE)
    member = models.ForeignKey("v1.Patient", on_delete=models.CASCADE)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    locked = models.BooleanField(default=False)

    def __str__(self) -> str:
        return (
            f"PatientGroupMember(patient_group={self.patient_group.id}, patient={self.member.id})"
        )


__exports__ = (
    "PatientGroup",
    "PatientGroupMember",
)
