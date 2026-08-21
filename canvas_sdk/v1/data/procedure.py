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


class ProcedureStatus(models.IntegerChoices):
    """Status of a Procedure."""

    IN_PROGRESS = 1, "in-progress"
    ABORTED = 2, "aborted"
    COMPLETED = 3, "completed"


class ProcedureQuerySet(
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
    ValueSetLookupQuerySet,
):
    """ProcedureQuerySet."""

    pass


ProcedureManager = BaseModelManager.from_queryset(ProcedureQuerySet)


class Procedure(AuditedModel, IdentifiableModel):
    """A procedure performed on or ordered for a patient."""

    class Meta:
        db_table = "canvas_sdk_data_api_procedure_001"

    objects = cast(ProcedureQuerySet, ProcedureManager())

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="procedures"
    )
    note = models.ForeignKey("v1.Note", on_delete=models.DO_NOTHING, related_name="procedures")
    provider = models.ForeignKey(
        "v1.Staff", on_delete=models.DO_NOTHING, related_name="procedures", null=True, default=None
    )
    status = models.IntegerField(choices=ProcedureStatus.choices, null=True)
    notes = models.TextField(null=True)


class ProcedureCoding(Coding):
    """A coding (e.g. CPT) recorded against a Procedure."""

    class Meta:
        db_table = "canvas_sdk_data_api_procedurecoding_001"

    procedure = models.ForeignKey(Procedure, on_delete=models.DO_NOTHING, related_name="codings")


__exports__ = ("Procedure", "ProcedureCoding", "ProcedureStatus")
