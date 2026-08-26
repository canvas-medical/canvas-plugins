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


class RemoveAllergyEventQuerySet(
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
    BaseQuerySet,
):
    """RemoveAllergyEventQuerySet."""

    pass


RemoveAllergyEventManager = BaseModelManager.from_queryset(RemoveAllergyEventQuerySet)


class RemoveAllergyEvent(AuditedModel, IdentifiableModel):
    """A record of an allergy being removed — the anchor for the remove_allergy command."""

    class Meta:
        db_table = "canvas_sdk_data_api_removeallergyevent_001"

    objects = cast(RemoveAllergyEventQuerySet, RemoveAllergyEventManager())

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="removed_allergies"
    )
    note = models.ForeignKey(
        "v1.Note", on_delete=models.DO_NOTHING, related_name="removed_allergies"
    )
    allergy = models.ForeignKey(
        "v1.AllergyIntolerance",
        on_delete=models.DO_NOTHING,
        related_name="remove_allergy_events",
        null=True,
    )
    rationale = models.CharField(max_length=1024, default="", blank=True)


__exports__ = ("RemoveAllergyEvent",)
