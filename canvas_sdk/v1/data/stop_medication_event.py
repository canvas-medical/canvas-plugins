from django.db import models

from canvas_sdk.v1.data.base import AuditedModel, IdentifiableModel


class StopMedicationEvent(AuditedModel, IdentifiableModel):
    """StopMedicationEvent."""

    class Meta:
        db_table = "canvas_sdk_data_api_stopmedicationevent_001"

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="stopped_medications"
    )
    note = models.ForeignKey(
        "v1.Note", on_delete=models.DO_NOTHING, related_name="stopped_medications"
    )
    medication = models.ForeignKey(
        "v1.Medication",
        on_delete=models.DO_NOTHING,
        related_name="stopmedicationevent_set",
        null=True,
    )
    rationale = models.CharField(max_length=1024, default="")


__exports__ = ("StopMedicationEvent",)
