from operator import attrgetter
from typing import Self, cast

from django.db import models
from django.db.models import Prefetch, TextChoices

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

    def with_latest_sig(self) -> Self:
        """Prefetch the sources ``latest_sig`` reads so it resolves without a per-medication query.

        Batches the active prescriptions and non-entered-in-error change medications (each with
        their note via ``select_related("note")``, deferring the large note body fields) plus the
        medication statements, mirroring the home-app ``resolve_latest_sig`` GraphQL hint.
        """
        from canvas_sdk.v1.data.change_medication import ChangeMedication
        from canvas_sdk.v1.data.prescription import Prescription

        deferred_note_body = ("note___body", "note___body_content", "note___body_order")
        return self.prefetch_related(
            Prefetch(
                "prescriptions",
                queryset=Prescription.objects.active()
                .select_related("note")
                .defer(*deferred_note_body),
                to_attr="_latest_sig_prescriptions",
            ),
            Prefetch(
                "change_medications",
                queryset=ChangeMedication.objects.filter(entered_in_error__isnull=True)
                .select_related("note")
                .defer(*deferred_note_body),
                to_attr="_latest_sig_change_medications",
            ),
            Prefetch("medication_statements", to_attr="_latest_sig_medication_statements"),
        )


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

        Reads the relations prefetched by ``Medication.objects.with_latest_sig()`` when present,
        falling back to live queries otherwise; use that helper to avoid an N+1 over medications.
        """
        if not self.dbid:
            return ""

        if hasattr(self, "_latest_sig_prescriptions"):
            latest_prescription = max(
                self._latest_sig_prescriptions, key=attrgetter("dbid"), default=None
            )
        else:
            latest_prescription = (
                self.prescriptions.active().select_related("note").order_by("-dbid").first()
            )
        if hasattr(self, "_latest_sig_change_medications"):
            latest_change_medication = max(
                self._latest_sig_change_medications, key=attrgetter("dbid"), default=None
            )
        else:
            latest_change_medication = (
                self.change_medications.filter(entered_in_error__isnull=True)
                .select_related("note")
                .order_by("-dbid")
                .first()
            )

        if latest_prescription and latest_change_medication:
            if (
                latest_prescription.note
                and latest_prescription.note.datetime_of_service
                > latest_change_medication.note.datetime_of_service
            ):
                return latest_prescription.combined_sig
            return latest_change_medication.sig_original_input
        if latest_prescription:
            return latest_prescription.combined_sig
        if latest_change_medication:
            return latest_change_medication.sig_original_input

        if hasattr(self, "_latest_sig_medication_statements"):
            latest_statement = max(
                self._latest_sig_medication_statements, key=attrgetter("dbid"), default=None
            )
        else:
            latest_statement = self.medication_statements.order_by("-dbid").first()
        if latest_statement:
            return latest_statement.sig_original_input
        return ""


class MedicationCoding(Coding):
    """MedicationCoding."""

    class Meta:
        db_table = "canvas_sdk_data_api_medicationcoding_001"

    medication = models.ForeignKey(
        Medication, on_delete=models.DO_NOTHING, related_name="codings", null=True
    )


__exports__ = ("Status", "Medication", "MedicationCoding")
