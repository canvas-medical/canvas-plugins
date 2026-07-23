from typing import cast

from django.db import models

from canvas_sdk.v1.data.base import (
    AuditedModel,
    CommittableModelManager,
    CommittableQuerySet,
    IdentifiableModel,
)


class ChangeMedication(AuditedModel, IdentifiableModel):
    """ChangeMedication."""

    class Meta:
        db_table = "canvas_sdk_data_api_changemedication_001"

    objects = cast(CommittableQuerySet, CommittableModelManager())

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.CASCADE, related_name="change_medications"
    )
    note = models.ForeignKey("v1.Note", on_delete=models.CASCADE, related_name="change_medications")
    medication = models.ForeignKey(
        "v1.Medication",
        on_delete=models.CASCADE,
        related_name="change_medications",
        null=True,
    )
    sig_original_input = models.CharField(max_length=1000, blank=True, default="")


__exports__ = ("ChangeMedication",)
