from typing import cast

from django.db import models

from canvas_sdk.v1.data.base import (
    AuditedModel,
    BaseModelManager,
    BaseQuerySet,
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
    IdentifiableModel,
)


class RemovePastMedicalHistoryEventQuerySet(
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
    BaseQuerySet,
):
    """RemovePastMedicalHistoryEventQuerySet."""

    pass


RemovePastMedicalHistoryEventManager = BaseModelManager.from_queryset(
    RemovePastMedicalHistoryEventQuerySet
)


class RemovePastMedicalHistoryEvent(AuditedModel, IdentifiableModel):
    """A record of a past medical history entry being removed — the anchor for the remove_past_medical_history command."""

    class Meta:
        db_table = "canvas_sdk_data_api_removepastmedicalhistoryevent_001"

    objects = cast(RemovePastMedicalHistoryEventQuerySet, RemovePastMedicalHistoryEventManager())

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="removed_past_medical_history"
    )
    note = models.ForeignKey(
        "v1.Note", on_delete=models.DO_NOTHING, related_name="removed_past_medical_history"
    )
    condition = models.ForeignKey(
        "v1.Condition",
        on_delete=models.DO_NOTHING,
        related_name="past_medical_history_removals",
        null=True,
    )
    rationale = models.CharField(max_length=512, default="", blank=True)


__exports__ = ("RemovePastMedicalHistoryEvent",)
