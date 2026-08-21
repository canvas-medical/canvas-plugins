from typing import cast

from django.db import models

from canvas_sdk.v1.data.base import (
    AuditedModel,
    CommittableModelManager,
    CommittableQuerySet,
    IdentifiableModel,
    TypeAheadNarrativeMixin,
)


class HistoryOfPresentIllness(TypeAheadNarrativeMixin, AuditedModel, IdentifiableModel):
    """History of Present Illness (HPI) recorded on a note."""

    class Meta:
        db_table = "canvas_sdk_data_api_historyofpresentillness_001"

    objects = cast(CommittableQuerySet, CommittableModelManager())

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="histories_of_present_illness"
    )
    note = models.ForeignKey(
        "v1.Note", on_delete=models.DO_NOTHING, related_name="histories_of_present_illness"
    )


__exports__ = ("HistoryOfPresentIllness",)
