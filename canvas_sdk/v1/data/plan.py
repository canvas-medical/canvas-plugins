from typing import cast

from django.db import models

from canvas_sdk.v1.data.base import (
    AuditedModel,
    CommittableModelManager,
    CommittableQuerySet,
    IdentifiableModel,
    TypeAheadNarrativeMixin,
)


class Plan(TypeAheadNarrativeMixin, AuditedModel, IdentifiableModel):
    """A Plan (plan of care) recorded on a note."""

    class Meta:
        db_table = "canvas_sdk_data_api_plan_001"

    objects = cast(CommittableQuerySet, CommittableModelManager())

    patient = models.ForeignKey("v1.Patient", on_delete=models.DO_NOTHING, related_name="plans")
    note = models.ForeignKey("v1.Note", on_delete=models.DO_NOTHING, related_name="plans")


__exports__ = ("Plan",)
