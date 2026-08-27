from typing import cast

from django.db import models

from canvas_sdk.v1.data.base import (
    AuditedModel,
    CommittableModelManager,
    CommittableQuerySet,
    IdentifiableModel,
)
from canvas_sdk.v1.data.encounter import EncounterMedium


class FollowUp(AuditedModel, IdentifiableModel):
    """A Follow Up recorded on a note — the anchor for the follow_up command."""

    class Meta:
        db_table = "canvas_sdk_data_api_followup_001"

    objects = cast(CommittableQuerySet, CommittableModelManager())

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="follow_ups"
    )
    note = models.ForeignKey("v1.Note", on_delete=models.DO_NOTHING, related_name="follow_ups")
    appointment_note = models.OneToOneField(
        "v1.Note", on_delete=models.DO_NOTHING, null=True, related_name="appointment_request"
    )
    requested_appointment_date = models.DateField(null=True, blank=True)
    requested_appointment_date_original_input = models.CharField(
        max_length=50, blank=True, default=""
    )
    reason_for_visit = models.TextField(default="", blank=True)
    reason_for_visit_coding = models.TextField(default="", blank=True)
    note_to_patient = models.TextField(default="", blank=True)
    internal_comment = models.TextField(default="", blank=True)
    requested_appointment_type = models.CharField(
        max_length=20,
        choices=EncounterMedium.choices,
        default=EncounterMedium.OFFICE,
        null=True,
        db_index=True,
    )
    requested_note_type = models.ForeignKey(
        "v1.NoteType", on_delete=models.DO_NOTHING, related_name="follow_ups"
    )


__exports__ = ("FollowUp",)
