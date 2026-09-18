from typing import cast

from django.db import models

from canvas_sdk.v1.data.base import (
    AuditedModel,
    CommittableModelManager,
    CommittableQuerySet,
    IdentifiableModel,
)


class PrivateNote(AuditedModel, IdentifiableModel):
    """A Private Note — the anchor for the PrivateNotes command.

    Private notes are clinician-only, so the note text is intentionally not exposed; this model
    surfaces only the anchor (patient, note, and audit fields).
    """

    class Meta:
        db_table = "canvas_sdk_data_api_privatenote_001"

    objects = cast(CommittableQuerySet, CommittableModelManager())

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="private_notes"
    )
    note = models.ForeignKey("v1.Note", on_delete=models.DO_NOTHING, related_name="private_notes")


__exports__ = ("PrivateNote",)
