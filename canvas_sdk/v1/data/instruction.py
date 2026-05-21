from typing import cast

from django.db import models

from canvas_sdk.v1.data.base import (
    AuditedModel,
    BaseModelManager,
    BaseQuerySet,
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
    IdentifiableModel,
    ValueSetLookupQuerySetMixin,
)
from canvas_sdk.v1.data.coding import Coding


class InstructionQuerySet(
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
    ValueSetLookupQuerySetMixin,
    BaseQuerySet,
):
    """InstructionQuerySet."""


InstructionManager = BaseModelManager.from_queryset(InstructionQuerySet)


class Instruction(AuditedModel, IdentifiableModel):
    """Instruction."""

    class Meta:
        db_table = "canvas_sdk_data_api_instruction_001"

    objects = cast(InstructionQuerySet, InstructionManager())

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="instructions"
    )
    note = models.ForeignKey("v1.Note", on_delete=models.DO_NOTHING, related_name="instructions")
    narrative = models.CharField(max_length=4000)


class InstructionCoding(Coding):
    """InstructionCoding."""

    class Meta:
        db_table = "canvas_sdk_data_api_instructioncoding_001"

    instruction = models.ForeignKey(
        Instruction, on_delete=models.DO_NOTHING, related_name="codings", null=True
    )


__exports__ = ("Instruction", "InstructionCoding")
