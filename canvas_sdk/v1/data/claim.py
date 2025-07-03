from decimal import Decimal
from typing import TYPE_CHECKING, Self

from django.db import models

from canvas_sdk.v1.data.common import PersonSex
from canvas_sdk.v1.data.coverage import CoverageRelationshipCode, CoverageType
from canvas_sdk.v1.data.fields import ChoiceArrayField
from canvas_sdk.v1.data.utils import quantize

if TYPE_CHECKING:
    from canvas_sdk.v1.data.claim_line_item import ClaimLineItemQuerySet


class InstallmentPlanStatus(models.TextChoices):
    """InstallmentPlanStatus."""

    ACTIVE = "active", "Active"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class InstallmentPlan(models.Model):
    """InstallmentPlan."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_quality_and_revenue_installmentplan_001"

    dbid = models.BigIntegerField(primary_key=True)

    creator = models.ForeignKey("v1.CanvasUser", on_delete=models.CASCADE)
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.CASCADE, related_name="installment_plans"
    )
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(choices=InstallmentPlanStatus.choices, max_length=10)
    expected_payoff_date = models.DateField()

    created = models.DateTimeField()
    modified = models.DateTimeField()


class ClaimQueueColumns(models.TextChoices):
    """ClaimQueueColumns."""

    NOTE_TYPE = "NoteType", "Note type"
    CLAIM_ID = "ClaimID", "Claim ID"
    DOS = "DateOfService", "Date of service"
    PATIENT = "Patient", "Patient"
    ACTIVE_INSURANCE = "ActiveInsurance", "Active insurance"
    INSURANCE_BALANCE = "InsuranceBalance", "Insurance balance"
    PATIENT_BALANCE = "PatientBalance", "Patient balance"
    DAYS_IN_QUEUE = "DaysInQueue", "Days in queue"
    PROVIDER = "Provider", "Provider"
    GUARANTOR = "Guarantor", "Guarantor"
    LATEST_REMIT = "LatestRemit", "Latest remit"
    LAST_INVOICED = "LastInvoiced", "Last invoiced"
    SNOOZED_UNTIL = "SnoozedUntil", "Snoozed until"
    LABELS = "Labels", "Labels"


class ClaimQueues(models.IntegerChoices):
    """ClaimQueues."""

    APPOINTMENT = 1, "Appointment"
    NEEDS_CLINICIAN_REVIEW = 2, "NeedsClinicianReview"
    NEEDS_CODING_REVIEW = 3, "NeedsCodingReview"
    QUEUED_FOR_SUBMISSION = 4, "QueuedForSubmission"
    FILED_AWAITING_RESPONSE = 5, "FiledAwaitingResponse"
    REJECTED_NEEDS_REVIEW = 6, "RejectedNeedsReview"
    ADJUDICATED_OPEN_BALANCE = 7, "AdjudicatedOpenBalance"
    PATIENT_BALANCE = 8, "PatientBalance"
    ZERO_BALANCE = 9, "ZeroBalance"
    TRASH = 10, "Trash"


class ClaimQueue(models.Model):
    """ClaimQueue."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_quality_and_revenue_queue_001"

    dbid = models.BigIntegerField(primary_key=True)
    queue_sort_ordering = models.IntegerField()
    name = models.CharField()
    display_name = models.CharField()
    description = models.CharField()
    show_in_revenue = models.BooleanField()
    visible_columns = ChoiceArrayField(models.CharField(choices=ClaimQueueColumns.choices))

    created = models.DateTimeField()
    modified = models.DateTimeField()


class ClaimPayerOrder(models.TextChoices):
    """ClaimPayerOrder."""

    PRIMARY = "Primary", "Primary"
    SECONDARY = "Secondary", "Secondary"
    TERTIARY = "Tertiary", "Tertiary"
    QUATERNARY = "Quaternary", "Quaternary"
    QUINARY = "Quinary", "Quinary"


class ClaimTypeCode(models.TextChoices):
    """ClaimTypeCode."""

    WORKING_AGED = "12", "Working Aged (Age 65 or older)"
    ESRD = "13", "End-Stage Renal Disease"
    NO_FAULT = "14", "No-fault"
    WORKERS_COMP = "15", "Workers Compensation"
    BLACK_LUNG = "41", "Black Lung"
    VA = "42", "Veterans Administration"
    DISABLED = "43", "Disabled (Under Age 65)"
    OTHER_LIABILITY = "47", "Other Liability Insurance is primary"
    UNNECESSARY = "", "No Typecode necessary"


class ClaimCoverageQuerySet(models.QuerySet):
    """ClaimCoverageQuerySet."""

    def active(self) -> Self:
        """Filter active claim coverages."""
        return self.filter(active=True)


class ClaimCoverage(models.Model):
    """A model that represents the link between a claim and a specific insurance coverage."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_quality_and_revenue_claimcoverage_001"

    objects = ClaimCoverageQuerySet.as_manager()

    dbid = models.BigIntegerField(primary_key=True)

    claim = models.ForeignKey("Claim", on_delete=models.CASCADE, related_name="coverages")

    coverage = models.ForeignKey(
        "v1.Coverage", related_name="claim_coverages", on_delete=models.PROTECT
    )

    active = models.BooleanField()
    payer_name = models.CharField()
    payer_id = models.CharField()
    payer_typecode = models.CharField()
    payer_order = models.CharField(choices=ClaimPayerOrder.choices)
    payer_addr1 = models.CharField()
    payer_addr2 = models.CharField()
    payer_city = models.CharField()
    payer_state = models.CharField()
    payer_zip = models.CharField()
    payer_plan_type = models.CharField(choices=ClaimTypeCode.choices)
    coverage_type = models.CharField(choices=CoverageType.choices)

    subscriber_employer = models.CharField()
    subscriber_group = models.CharField()
    subscriber_number = models.CharField()
    subscriber_plan = models.CharField()
    subscriber_dob = models.CharField()
    subscriber_first_name = models.CharField()
    subscriber_last_name = models.CharField()
    subscriber_middle_name = models.CharField()
    subscriber_phone = models.CharField()
    subscriber_sex = models.CharField(choices=PersonSex.choices)
    subscriber_addr1 = models.CharField()
    subscriber_addr2 = models.CharField()
    subscriber_city = models.CharField()
    subscriber_state = models.CharField()
    subscriber_zip = models.CharField()
    subscriber_country = models.CharField()
    patient_relationship_to_subscriber = models.CharField(choices=CoverageRelationshipCode.choices)

    pay_to_addr1 = models.CharField()
    pay_to_addr2 = models.CharField()
    pay_to_city = models.CharField()
    pay_to_state = models.CharField()
    pay_to_zip = models.CharField()

    resubmission_code = models.CharField()
    payer_icn = models.CharField()

    created = models.DateTimeField()
    modified = models.DateTimeField()


class ClaimPatient(models.Model):
    """ClaimPatient."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_quality_and_revenue_claimpatient_001"

    dbid = models.BigIntegerField(primary_key=True)
    claim = models.OneToOneField("v1.Claim", on_delete=models.CASCADE, related_name="patient")
    photo = models.CharField()
    dob = models.CharField()
    first_name = models.CharField()
    last_name = models.CharField()
    middle_name = models.CharField()
    phone = models.CharField()
    sex = models.CharField(choices=PersonSex.choices)
    ssn = models.CharField()
    addr1 = models.CharField()
    addr2 = models.CharField()
    city = models.CharField()
    state = models.CharField()
    zip = models.CharField()
    country = models.CharField()

    created = models.DateTimeField()
    modified = models.DateTimeField()


class ClaimQueryset(models.QuerySet):
    """ClaimQueryset."""

    def active(self) -> Self:
        """Active claims."""
        return self.exclude(current_queue__queue_sort_ordering=ClaimQueues.TRASH)


class Claim(models.Model):
    """Claim."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_quality_and_revenue_claim_001"

    objects = ClaimQueryset.as_manager()

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    note = models.ForeignKey("v1.Note", on_delete=models.PROTECT, related_name="claims", null=True)
    installment_plan = models.ForeignKey(
        InstallmentPlan, on_delete=models.SET_NULL, related_name="claims", null=True
    )
    current_queue = models.ForeignKey(ClaimQueue, on_delete=models.PROTECT, related_name="claims")
    latest_invoice = models.ForeignKey("v1.Invoice", on_delete=models.SET_NULL, null=True)
    current_coverage = models.ForeignKey(
        ClaimCoverage, related_name="claims", on_delete=models.SET_NULL, null=True
    )

    accept_assign = models.BooleanField()
    auto_accident = models.BooleanField()
    auto_accident_state = models.CharField()
    employment_related = models.BooleanField()
    other_accident = models.BooleanField()
    accident_code = models.CharField()
    illness_date = models.DateField()
    remote_batch_id = models.CharField()
    remote_file_id = models.CharField()
    prior_auth = models.CharField()

    narrative = models.CharField()
    account_number = models.CharField()
    snoozed_until = models.DateField()

    patient_balance = models.DecimalField(max_digits=8, decimal_places=2)
    aggregate_coverage_balance = models.DecimalField(max_digits=8, decimal_places=2)
    created = models.DateTimeField()
    modified = models.DateTimeField()

    @property
    def total_charges(self) -> Decimal:
        """Total charges for the claim."""
        line_items = self.get_active_claim_line_items()
        if line_items:
            return quantize(sum(line_item.charge for line_item in line_items))
        return Decimal("0.00")

    @property
    def total_paid(self) -> Decimal | int:
        """Total paid amount for the claim."""
        return sum(posting.paid_amount for posting in self.postings.active()) or Decimal("0.00")

    @property
    def total_adjusted(self) -> Decimal | int:
        """Total adjusted amount for the claim."""
        return sum(
            posting.adjusted_and_transferred_amount for posting in self.postings.active()
        ) or Decimal("0.00")

    @property
    def balance(self) -> Decimal:
        """Balance for the claim."""
        return self.aggregate_coverage_balance + self.patient_balance

    @property
    def total_patient_paid(self) -> Decimal | int:
        """Total amount paid by the patient."""
        return sum(posting.paid_amount for posting in self.patient.postings.active()) or Decimal(
            "0.00"
        )

    @property
    def total_payer_paid(self) -> Decimal | int:
        """Total amount paid by the coverages."""
        return sum(
            posting.paid_amount
            for coverage in self.coverages.active()
            for posting in coverage.postings.active()
        ) or Decimal("0.00")

    def get_active_claim_line_items(self) -> "ClaimLineItemQuerySet":
        """Return the active claim line items."""
        return self.line_items.active().exclude_copay_and_unlinked()


__exports__ = (
    "Claim",
    "ClaimQueue",
    "ClaimCoverage",
    "ClaimPatient",
    "ClaimPayerOrder",
    "ClaimQueues",
    "ClaimQueueColumns",
    "ClaimTypeCode",
    "InstallmentPlan",
    "InstallmentPlanStatus",
)
