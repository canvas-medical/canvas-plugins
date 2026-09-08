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


class ResolveConditionEventQuerySet(
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
    BaseQuerySet,
):
    """ResolveConditionEventQuerySet."""

    pass


ResolveConditionEventManager = BaseModelManager.from_queryset(ResolveConditionEventQuerySet)


class ResolveConditionEvent(AuditedModel, IdentifiableModel):
    """A record of a condition being resolved — the anchor for the resolve_condition command."""

    class Meta:
        db_table = "canvas_sdk_data_api_resolveconditionevent_001"

    objects = cast(ResolveConditionEventQuerySet, ResolveConditionEventManager())

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="resolved_conditions"
    )
    note = models.ForeignKey(
        "v1.Note", on_delete=models.DO_NOTHING, related_name="resolved_conditions"
    )
    condition = models.ForeignKey(
        "v1.Condition", on_delete=models.DO_NOTHING, related_name="resolutions", null=True
    )
    rationale = models.CharField(max_length=1024, default="", blank=True)
    show_in_condition_list = models.BooleanField(default=False)


__exports__ = ("ResolveConditionEvent",)
