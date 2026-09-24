from typing import cast

from django.db import models

from canvas_sdk.v1.data.base import (
    AuditedModel,
    CommittableModelManager,
    CommittableQuerySet,
    IdentifiableModel,
)


class Clipboard(AuditedModel, IdentifiableModel):
    """The anchor for the Clipboard command — free-text content staged on a note."""

    class Meta:
        db_table = "canvas_sdk_data_api_clipboard_001"

    objects = cast(CommittableQuerySet, CommittableModelManager())

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="clipboards"
    )
    note = models.ForeignKey("v1.Note", on_delete=models.DO_NOTHING, related_name="clipboards")
    text = models.TextField(default="", blank=True)


__exports__ = ("Clipboard",)
