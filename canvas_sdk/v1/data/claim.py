from decimal import Decimal
from typing import TYPE_CHECKING, Self

from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, Model
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


class InstallmentPlan(Model):
    """InstallmentPlan."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_installmentplan_001"

    creator = models.ForeignKey("v1.CanvasUser", on_delete=models.CASCADE)
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.CASCADE, related_name="installment_plans"
    )
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(choices=InstallmentPlanStatus.choices, max_length=10)
    expected_payoff_date = models.DateField()

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


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


class ClaimQueue(Model):
    """ClaimQueue."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_queue_001"

    queue_sort_ordering = models.IntegerField()
    name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    show_in_revenue = models.BooleanField()
    visible_columns = ChoiceArrayField(
        models.CharField(choices=ClaimQueueColumns.choices, max_length=64)
    )

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


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


class ClaimCoverage(Model):
    """A model that represents the link between a claim and a specific insurance coverage."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_claimcoverage_001"

    objects = ClaimCoverageQuerySet.as_manager()

    claim = models.ForeignKey("Claim", on_delete=models.CASCADE, related_name="coverages")

    coverage = models.ForeignKey(
        "v1.Coverage", related_name="claim_coverages", on_delete=models.PROTECT
    )

    active = models.BooleanField()
    payer_name = models.CharField(max_length=255)
    payer_id = models.CharField(max_length=255)
    payer_typecode = models.CharField(max_length=2)
    payer_order = models.CharField(choices=ClaimPayerOrder.choices, max_length=10)
    payer_addr1 = models.CharField(max_length=255)
    payer_addr2 = models.CharField(max_length=255)
    payer_city = models.CharField(max_length=255)
    payer_state = models.CharField(max_length=2)
    payer_zip = models.CharField(max_length=255)
    payer_plan_type = models.CharField(choices=ClaimTypeCode.choices, max_length=20)
    coverage_type = models.CharField(choices=CoverageType.choices, max_length=64)

    subscriber_employer = models.CharField(max_length=255)
    subscriber_group = models.CharField(max_length=255)
    subscriber_number = models.CharField(max_length=100)
    subscriber_plan = models.CharField(max_length=255)
    subscriber_dob = models.CharField(max_length=10)
    subscriber_first_name = models.CharField(max_length=255)
    subscriber_last_name = models.CharField(max_length=255)
    subscriber_middle_name = models.CharField(max_length=255)
    subscriber_phone = models.CharField(max_length=50)
    subscriber_sex = models.CharField(choices=PersonSex.choices, max_length=3)
    subscriber_addr1 = models.CharField(max_length=255)
    subscriber_addr2 = models.CharField(max_length=255)
    subscriber_city = models.CharField(max_length=255)
    subscriber_state = models.CharField(max_length=2)
    subscriber_zip = models.CharField(max_length=255)
    subscriber_country = models.CharField(max_length=50)
    patient_relationship_to_subscriber = models.CharField(
        choices=CoverageRelationshipCode.choices, max_length=2
    )

    pay_to_addr1 = models.CharField(max_length=255)
    pay_to_addr2 = models.CharField(max_length=255)
    pay_to_city = models.CharField(max_length=255)
    pay_to_state = models.CharField(max_length=2)
    pay_to_zip = models.CharField(max_length=255)

    resubmission_code = models.CharField(max_length=1)
    payer_icn = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class ClaimPatient(Model):
    """ClaimPatient."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_claimpatient_001"

    claim = models.OneToOneField("v1.Claim", on_delete=models.CASCADE, related_name="patient")
    photo = models.CharField(max_length=512)
    dob = models.CharField(max_length=10)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    sex = models.CharField(choices=PersonSex.choices, max_length=3)
    ssn = models.CharField(max_length=10)
    addr1 = models.CharField(max_length=255)
    addr2 = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=2)
    zip = models.CharField(max_length=255)
    country = models.CharField(max_length=50)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class ClaimQueryset(models.QuerySet):
    """ClaimQueryset."""

    def active(self) -> Self:
        """Active claims."""
        return self.exclude(current_queue__queue_sort_ordering=ClaimQueues.TRASH)


class Claim(IdentifiableModel):
    """Claim."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_claim_001"

    objects = ClaimQueryset.as_manager()

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
    auto_accident_state = models.CharField(max_length=2)
    employment_related = models.BooleanField()
    other_accident = models.BooleanField()
    accident_code = models.CharField(max_length=10)
    illness_date = models.DateField()
    remote_batch_id = models.CharField(max_length=100)
    remote_file_id = models.CharField(max_length=100)
    prior_auth = models.CharField(max_length=100)

    narrative = models.CharField(max_length=2500)
    account_number = models.CharField(max_length=255)
    snoozed_until = models.DateField()

    patient_balance = models.DecimalField(max_digits=8, decimal_places=2)
    aggregate_coverage_balance = models.DecimalField(max_digits=8, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

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
