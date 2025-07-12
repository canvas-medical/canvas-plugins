from decimal import Decimal
from typing import Self

from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, Model
from canvas_sdk.v1.data.utils import quantize


class PostingQuerySet(models.QuerySet):
    """A queryset for CoveragePosting objects."""

    def active(self) -> Self:
        """Return a queryset that filters for active postings."""
        return self.filter(entered_in_error__isnull=True)


class BasePosting(Model):
    """
    Base model to aggregate multiple line item transactions on a claim.
    """

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_baseposting_001"

    objects = PostingQuerySet.as_manager()

    corrected_posting = models.ForeignKey(
        "v1.BasePosting", related_name="correction_postings", on_delete=models.PROTECT, null=True
    )

    claim = models.ForeignKey("v1.Claim", related_name="postings", on_delete=models.PROTECT)
    payment_collection = models.ForeignKey(
        "v1.PaymentCollection", related_name="postings", null=True, on_delete=models.PROTECT
    )

    description = models.TextField(default="")

    entered_in_error = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.PROTECT, null=True, blank=True
    )

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    @property
    def paid_amount(self) -> Decimal:
        """Returns the total amount paid for this posting."""
        return quantize(sum(lip.amount for lip in self.newlineitempayments.all()))

    @property
    def contractual_adjusted_amount(self) -> Decimal:
        """Returns the total amount of contractual adjustments for this posting."""
        return quantize(
            sum(lia.amount for lia in self.newlineitemadjustments.all() if lia.write_off)
        )

    @property
    def non_write_off_adjusted_amount(self) -> Decimal | int:
        """Returns the total amount of non-write-off adjustments for this posting."""
        return sum(lia.amount for lia in self.newlineitemadjustments.all() if not lia.write_off)

    @property
    def transferred_amount(self) -> Decimal:
        """Returns the total amount transferred for this posting."""
        return quantize(sum(lit.amount for lit in self.lineitemtransfers.all()))

    @property
    def transferred_to_patient_amount(self) -> Decimal | int:
        """Returns the total amount transferred to the patient."""
        transfers = [trans for trans in self.lineitemtransfers.all() if trans.transfer_to_patient]
        return sum(lit.amount for lit in transfers)

    @property
    def transferred_to_coverage_amount(self) -> Decimal | int:
        """Returns the total amount transferred to another coverage."""
        transfers = [trans for trans in self.lineitemtransfers.all() if trans.transfer_to]
        return sum(lit.amount for lit in transfers)

    @property
    def adjusted_and_transferred_amount(self) -> Decimal:
        """Returns the charges amount per claim for a patient posting."""
        return self.contractual_adjusted_amount + self.transferred_amount

    @property
    def posted_amount(self) -> Decimal:
        """Property to compute how much was posted with this posting: sums all payments and write-off adjustments."""
        return self.paid_amount + self.contractual_adjusted_amount + self.transferred_amount


class CoveragePosting(BasePosting):
    """Represents an insurance payment/adjustment on a claim level."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_coverageposting_001"

    remittance = models.ForeignKey(
        "v1.BaseRemittanceAdvice", related_name="postings", on_delete=models.PROTECT, null=True
    )
    claim_coverage = models.ForeignKey(
        "v1.ClaimCoverage", related_name="postings", on_delete=models.PROTECT
    )

    crossover_carrier = models.CharField(max_length=255)
    crossover_id = models.CharField(max_length=255)
    payer_icn = models.CharField(max_length=255)
    position_in_era = models.PositiveIntegerField()


class PatientPosting(BasePosting):
    """A model that represents a patient payment/adjustment on a claim level."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_patientposting_001"

    claim_patient = models.ForeignKey(
        "v1.ClaimPatient", related_name="postings", on_delete=models.PROTECT
    )
    patient_payment = models.ForeignKey(
        "v1.BulkPatientPosting", related_name="postings", on_delete=models.PROTECT, null=True
    )

    copay = models.ForeignKey(
        "v1.BulkPatientPosting", related_name="copays", on_delete=models.PROTECT, null=True
    )

    @property
    def discounted_amount(self) -> Decimal:
        """Returns the discounted amount per claim for a patient bulk posting."""
        if not self.patient_payment or not self.patient_payment.discount:
            return Decimal("0")

        discount = self.patient_payment.discount
        return quantize(
            sum(
                lia.amount
                for lia in self.newlineitemadjustments.all()
                if (
                    lia.write_off
                    and (lia.group, lia.code)
                    == (discount.adjustment_group, discount.adjustment_code)
                )
            )
        )

    @property
    def charges_amount(self) -> Decimal:
        """Returns the charges amount per claim for a patient posting."""
        return self.discounted_amount + self.paid_amount


class AbstractBulkPosting(IdentifiableModel):
    """Patient and Insurance bulk posting shared columns."""

    class Meta:
        abstract = True

    payment_collection = models.OneToOneField(
        "v1.PaymentCollection", related_name="%(class)s", on_delete=models.PROTECT
    )

    total_paid = models.DecimalField(max_digits=8, decimal_places=2)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class BulkPatientPosting(AbstractBulkPosting):
    """Model to aggregate bulk patient payments on multiple claims."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_bulkpatientposting_001"

    discount = models.ForeignKey(
        "v1.Discount", related_name="patient_postings", null=True, on_delete=models.SET_NULL
    )
    payer = models.ForeignKey("v1.Patient", related_name="payments", on_delete=models.PROTECT)

    @property
    def total_posted_amount(self) -> Decimal:
        """Property to compute how much was posted with all associated postings."""
        postings = self.postings.active()
        return quantize(sum(posting.posted_amount for posting in postings))

    @property
    def discounted_amount(self) -> Decimal:
        """Returns the sum of discounted amounts for every posting created with this collection."""
        postings = self.postings.active()
        return quantize(sum(posting.discounted_amount for posting in postings))


class BaseRemittanceAdvice(AbstractBulkPosting):
    """Manual and Electronic Shared columns."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_baseremittanceadvice_001"

    transactor = models.ForeignKey(
        "v1.Transactor", related_name="remits", null=True, on_delete=models.PROTECT
    )

    era_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)

    @property
    def total_posted_amount(self) -> Decimal:
        """Property to compute how much was posted with all associated postings."""
        postings = self.postings.active()
        return quantize(sum(posting.posted_amount for posting in postings))


__exports__ = (
    "BasePosting",
    "CoveragePosting",
    "PatientPosting",
    "BulkPatientPosting",
    "BaseRemittanceAdvice",
)
