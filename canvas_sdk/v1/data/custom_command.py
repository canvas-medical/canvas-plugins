from typing import cast

from django.db import models

from canvas_sdk.v1.data.base import (
    AuditedModel,
    CommittableModelManager,
    CommittableQuerySet,
    IdentifiableModel,
)


class CustomCommand(AuditedModel, IdentifiableModel):
    """A Custom Command — the anchor for the custom_command SDK command."""

    class Meta:
        db_table = "canvas_sdk_data_api_customcommand_001"

    objects = cast(CommittableQuerySet, CommittableModelManager())

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="custom_commands"
    )
    note = models.ForeignKey("v1.Note", on_delete=models.DO_NOTHING, related_name="custom_commands")


__exports__ = ("CustomCommand",)
