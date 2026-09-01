from collections.abc import Container
from typing import cast

from django.db import models

from canvas_sdk.v1.data.base import (
    AuditedModel,
    BaseModelManager,
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
    IdentifiableModel,
    ValueSetLookupQuerySet,
)
from canvas_sdk.v1.data.coding import Coding


class FamilyHistoryQuerySet(
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
    ValueSetLookupQuerySet,
):
    """FamilyHistoryQuerySet."""

    @staticmethod
    def q_object(system: str, codes: Container[str]) -> models.Q:
        """FamilyHistoryCoding uses the singular ``coding`` reverse accessor (mirrors home-app)."""
        return models.Q(coding__system=system, coding__code__in=codes)


FamilyHistoryManager = BaseModelManager.from_queryset(FamilyHistoryQuerySet)


class FamilyHistory(AuditedModel, IdentifiableModel):
    """FamilyHistory — a patient's family medical history for one relative."""

    class Meta:
        db_table = "canvas_sdk_data_api_familyhistory_001"

    objects = cast(FamilyHistoryQuerySet, FamilyHistoryManager())

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="family_histories"
    )
    note = models.ForeignKey(
        "v1.Note", on_delete=models.DO_NOTHING, related_name="family_histories"
    )
    relation_snomed_code = models.BigIntegerField(db_index=True, null=True)
    relation_snomed_term = models.CharField(max_length=255, blank=True, default="")
    narrative = models.CharField(max_length=512, blank=True, default="")


class FamilyHistoryCoding(Coding):
    """FamilyHistoryCoding — a condition coding recorded against a FamilyHistory."""

    class Meta:
        db_table = "canvas_sdk_data_api_familyhistorycoding_001"

    family_history = models.ForeignKey(
        FamilyHistory, on_delete=models.DO_NOTHING, related_name="coding"
    )


__exports__ = ("FamilyHistory", "FamilyHistoryCoding")
