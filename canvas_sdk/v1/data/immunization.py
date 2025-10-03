from typing import Self, cast

from django.db import models

from canvas_sdk.v1.data.base import (
    BaseModelManager,
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
    IdentifiableModel,
    ValueSetLookupQuerySet,
)
from canvas_sdk.v1.data.coding import Coding


class ImmunizationStatus(models.TextChoices):
    """ImmunizationStatus."""

    STATUS_IN_PROGRESS = "in-progress", "In Progress"
    STATUS_ONHOLD = "on-hold"
    STATUS_COMPLETED = "completed"
    STATUS_STOPPED = "stopped"


class ImmunizationReasonsNotGiven(models.TextChoices):
    """ImmunizationReasonsNotGiven."""

    NA = "NA", "not applicable"
    IMMUNE = "IMMUNE", "immunity"
    MEDPREC = "MEDPREC", "medical precaution"
    OSTOCK = "OSTOCK", "product out of stock"
    PATOBJ = "PATOBJ", "patient objection"


class ImmunizationQuerySet(
    ValueSetLookupQuerySet, CommittableQuerySetMixin, ForPatientQuerySetMixin
):
    """ImmunizationQuerySet."""

    def active(self) -> Self:
        """Filter immunizations."""
        return self.committed()


ImmunizationManager = BaseModelManager.from_queryset(ImmunizationQuerySet)


class Immunization(IdentifiableModel):
    """Immunization."""

    class Meta:
        db_table = "canvas_sdk_data_api_immunization_001"

    objects = cast(ImmunizationQuerySet, ImmunizationManager())

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="immunizations", null=True
    )
    note = models.ForeignKey("v1.Note", on_delete=models.DO_NOTHING, related_name="immunizations")
    status = models.CharField(
        choices=ImmunizationStatus.choices,
        max_length=20,
        default=ImmunizationStatus.STATUS_IN_PROGRESS,
    )
    lot_number = models.CharField(max_length=20, blank=True, default="")
    manufacturer = models.CharField(max_length=100, blank=True, default="")
    exp_date_original = models.CharField(max_length=50, blank=True, default="")
    exp_date = models.DateField(null=True)
    sig_original = models.CharField(max_length=75, blank=True, default="")
    date_ordered = models.DateField(null=True)
    given_by = models.ForeignKey(
        "v1.Staff", on_delete=models.DO_NOTHING, related_name="immunizations_given", null=True
    )
    consent_given = models.BooleanField(default=False)
    take_quantity = models.FloatField(null=True)
    dose_form = models.CharField(max_length=255, blank=True, default="")
    route = models.CharField(max_length=255, blank=True, default="")
    frequency_normalized_per_day = models.FloatField(null=True)
    deleted = models.BooleanField()


class ImmunizationCoding(Coding):
    """ImmunizationCoding."""

    class Meta:
        db_table = "canvas_sdk_data_api_immunizationcoding_001"

    immunization = models.ForeignKey(
        Immunization, on_delete=models.DO_NOTHING, related_name="codings", null=True
    )


class ImmunizationStatementQuerySet(
    ValueSetLookupQuerySet, CommittableQuerySetMixin, ForPatientQuerySetMixin
):
    """ImmunizationStatementQuerySet."""

    def active(self) -> Self:
        """Filter immunizations statements."""
        return self.committed()


ImmunizationStatementManager = BaseModelManager.from_queryset(ImmunizationStatementQuerySet)


class ImmunizationStatement(IdentifiableModel):
    """ImmunizationStatement."""

    class Meta:
        db_table = "canvas_sdk_data_api_immunizationstatement_001"

    objects = cast(ImmunizationStatementQuerySet, ImmunizationStatementManager())

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="immunization_statements", null=True
    )
    note = models.ForeignKey(
        "v1.Note", on_delete=models.DO_NOTHING, related_name="immunization_statements"
    )
    date_original = models.CharField(max_length=50, blank=True, default="")
    date = models.DateField(null=True)
    evidence = models.CharField(max_length=255, blank=True, default="")
    comment = models.CharField(max_length=255, blank=True, default="")
    reason_not_given = models.CharField(
        max_length=20,
        choices=ImmunizationReasonsNotGiven.choices,
        default=ImmunizationReasonsNotGiven.NA,
    )
    deleted = models.BooleanField()


class ImmunizationStatementCoding(Coding):
    """ImmunizationStatementCoding."""

    class Meta:
        db_table = "canvas_sdk_data_api_immunizationstatementcoding_001"

    immunization_statement = models.ForeignKey(
        ImmunizationStatement, on_delete=models.CASCADE, related_name="coding"
    )


__exports__ = (
    "ImmunizationStatus",
    "ImmunizationReasonsNotGiven",
    "Immunization",
    "ImmunizationCoding",
    "ImmunizationStatement",
    "ImmunizationStatementCoding",
)
