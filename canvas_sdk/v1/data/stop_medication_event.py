from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel


class StopMedicationEvent(IdentifiableModel):
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
    entered_in_error = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, related_name="+", null=True
    )
    committer = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, related_name="+", null=True
    )
    originator = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, related_name="+")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    rationale = models.CharField(max_length=1024, default="")


__exports__ = ("StopMedicationEvent",)
