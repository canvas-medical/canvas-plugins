from operator import attrgetter
from typing import Self, cast

from django.db import models
from django.db.models import TextChoices

from canvas_sdk.v1.data.base import (
    BaseModelManager,
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
    IdentifiableModel,
    ValueSetLookupQuerySet,
)
from canvas_sdk.v1.data.coding import Coding


class Status(TextChoices):
    """Medication status."""

    ACTIVE = "active", "active"
    INACTIVE = "inactive", "inactive"


class MedicationQuerySet(CommittableQuerySetMixin, ForPatientQuerySetMixin, ValueSetLookupQuerySet):
    """MedicationQuerySet."""

    def active(self) -> Self:
        """Filter by active medications."""
        return self.committed().filter(status=Status.ACTIVE)


MedicationManager = BaseModelManager.from_queryset(MedicationQuerySet)


class Medication(IdentifiableModel):
    """Medication."""

    class Meta:
        db_table = "canvas_sdk_data_api_medication_001"

    objects = cast(MedicationQuerySet, MedicationManager())

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="medications", null=True
    )
    deleted = models.BooleanField()
    entered_in_error = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    committer = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    status = models.CharField(choices=Status.choices, max_length=20)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    quantity_qualifier_description = models.TextField()
    clinical_quantity_description = models.TextField()
    potency_unit_code = models.CharField(max_length=20)
    national_drug_code = models.CharField(max_length=20)
    erx_quantity = models.FloatField()

    @property
    def latest_sig(self) -> str:
        """Return the most recent sig across prescriptions, change medications, and statements.

        Ports the home-app ``Medication.latest_sig`` precedence: when both an active prescription
        and a non-entered-in-error change medication exist, the one whose note has the later date
        of service wins; otherwise the latest prescription, then the latest change medication, then
        the latest medication statement (each "latest" being the highest ``dbid``). Prescriptions
        contribute their ``combined_sig``. Returns an empty string when no source has a sig.
        """
        if not self.dbid:
            return ""

        prescriptions = list(self.prescriptions.active().order_by("-dbid"))
        change_medications = list(self.change_medications.filter(entered_in_error__isnull=True))
        medication_statements = list(self.medication_statements.all())

        if prescriptions and change_medications:
            latest_prescription = prescriptions[0]
            latest_change_med = max(change_medications, key=attrgetter("dbid"))
            if (
                latest_prescription.note.datetime_of_service
                > latest_change_med.note.datetime_of_service
            ):
                return latest_prescription.combined_sig
            return latest_change_med.sig_original_input
        if prescriptions:
            return prescriptions[0].combined_sig
        if change_medications:
            return max(change_medications, key=attrgetter("dbid")).sig_original_input
        if medication_statements:
            return max(medication_statements, key=attrgetter("dbid")).sig_original_input
        return ""


class MedicationCoding(Coding):
    """MedicationCoding."""

    class Meta:
        db_table = "canvas_sdk_data_api_medicationcoding_001"

    medication = models.ForeignKey(
        Medication, on_delete=models.DO_NOTHING, related_name="codings", null=True
    )


__exports__ = ("Status", "Medication", "MedicationCoding")
