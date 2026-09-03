from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel
from canvas_sdk.v1.data.patient_group import PatientGroup
from canvas_sdk.v1.data.team import Team


class Group(TimestampedModel, IdentifiableModel):
    """A Group — a stable external identifier over a Team or PatientGroup via a generic relation."""

    class Meta:
        db_table = "canvas_sdk_data_api_group_001"

    content_type = models.ForeignKey(
        "v1.ContentType", on_delete=models.DO_NOTHING, related_name="+", null=True
    )
    object_id = models.BigIntegerField(null=True)

    @property
    def team(self) -> Team | None:
        """The Team this group points at, when its content object is a Team."""
        if self.content_type and self.content_type.model == "team" and self.object_id:
            return Team.objects.filter(dbid=self.object_id).first()
        return None

    @property
    def patient_group(self) -> PatientGroup | None:
        """The PatientGroup this group points at, when its content object is a PatientGroup."""
        if self.content_type and self.content_type.model == "patientgroup" and self.object_id:
            return PatientGroup.objects.filter(dbid=self.object_id).first()
        return None


__exports__ = ("Group",)
