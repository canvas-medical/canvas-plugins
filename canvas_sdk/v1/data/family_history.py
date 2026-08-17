from typing import cast

from django.db import models

from canvas_sdk.v1.data.base import (
    BaseModelManager,
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
    IdentifiableModel,
    TimestampedModel,
    ValueSetLookupQuerySet,
)
from canvas_sdk.v1.data.coding import Coding


class FamilyHistoryQuerySet(
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
    ValueSetLookupQuerySet,
):
    """FamilyHistoryQuerySet."""

    pass


FamilyHistoryManager = BaseModelManager.from_queryset(FamilyHistoryQuerySet)


class FamilyHistory(TimestampedModel, IdentifiableModel):
    """FamilyHistory — a patient's family medical history for one relative."""

    class Meta:
        db_table = "canvas_sdk_data_api_familyhistory_001"

    objects = cast(FamilyHistoryQuerySet, FamilyHistoryManager())

    deleted = models.BooleanField()
    committer = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    entered_in_error = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="family_histories", null=True
    )
    note = models.ForeignKey(
        "v1.Note", on_delete=models.DO_NOTHING, related_name="family_histories", null=True
    )
    relation_snomed_code = models.BigIntegerField(null=True)
    relation_snomed_term = models.CharField(max_length=255)
    narrative = models.CharField(max_length=512)


class FamilyHistoryCoding(Coding):
    """FamilyHistoryCoding — a condition coding recorded against a FamilyHistory."""

    class Meta:
        db_table = "canvas_sdk_data_api_familyhistorycoding_001"

    family_history = models.ForeignKey(
        FamilyHistory, on_delete=models.DO_NOTHING, related_name="codings", null=True
    )


__exports__ = ("FamilyHistory", "FamilyHistoryCoding")
