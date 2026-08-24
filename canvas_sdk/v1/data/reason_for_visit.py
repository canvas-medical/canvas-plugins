from typing import cast

from django.contrib.postgres.fields import ArrayField
from django.db import models

from canvas_sdk.v1.data.base import (
    AuditedModel,
    CommittableModelManager,
    CommittableQuerySet,
    IdentifiableModel,
    TypeAheadNarrativeMixin,
)
from canvas_sdk.v1.data.coding import Coding


class ReasonForVisit(TypeAheadNarrativeMixin, AuditedModel, IdentifiableModel):
    """A Reason for Visit recorded on a note — the anchor for the reason_for_visit command."""

    class Meta:
        db_table = "canvas_sdk_data_api_reasonforvisit_001"

    objects = cast(CommittableQuerySet, CommittableModelManager())

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="reasons_for_visit"
    )
    note = models.ForeignKey(
        "v1.Note", on_delete=models.DO_NOTHING, related_name="reasons_for_visit"
    )


class ReasonForVisitCoding(Coding):
    """ReasonForVisitCoding."""

    class Meta:
        db_table = "canvas_sdk_data_api_reasonforvisitcoding_001"

    reason_for_visit = models.ForeignKey(
        ReasonForVisit, on_delete=models.DO_NOTHING, related_name="codings"
    )


class ReasonForVisitSettingCoding(IdentifiableModel, Coding):
    """ReasonForVisitSettingCoding."""

    class Meta:
        db_table = "canvas_sdk_data_api_reasonforvisitsettingcoding_001"

    objects: models.Manager["ReasonForVisitSettingCoding"]

    duration = ArrayField(models.DurationField())


__exports__ = ("ReasonForVisit", "ReasonForVisitCoding", "ReasonForVisitSettingCoding")
