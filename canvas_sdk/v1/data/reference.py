from typing import cast

from django.db import models

from canvas_sdk.v1.data.base import (
    AuditedModel,
    CommittableModelManager,
    CommittableQuerySet,
    IdentifiableModel,
)


class Reference(AuditedModel, IdentifiableModel):
    """A Reference — the anchor for the reference command."""

    class Meta:
        db_table = "canvas_sdk_data_api_reference_001"

    objects = cast(CommittableQuerySet, CommittableModelManager())

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="references"
    )
    note = models.ForeignKey("v1.Note", on_delete=models.DO_NOTHING, related_name="references")
    diagnostic_view = models.ForeignKey(
        "v1.DiagnosticView",
        on_delete=models.DO_NOTHING,
        related_name="references",
        null=True,
    )
    name = models.CharField(max_length=100, blank=True, default="")
    content = models.JSONField(blank=True, default=dict)


__exports__ = ("Reference",)
