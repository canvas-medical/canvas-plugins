from decimal import Decimal
from typing import Self, cast

from django.db import models

from canvas_sdk.v1.data.base import (
    BaseModelManager,
    CommittableModelManager,
    CommittableQuerySet,
    IdentifiableModel,
    Model,
    TimestampedModel,
)
from canvas_sdk.v1.data.utils import presigned_url, quantize


class PostingQuerySet(models.QuerySet):
    """A queryset for CoveragePosting objects."""

    def active(self) -> Self:
        """Return a queryset that filters for active postings."""
        return self.filter(entered_in_error__isnull=True)


class BasePosting(TimestampedModel):
    """
    Base model to aggregate multiple line item transactions on a claim.
    """

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_baseposting_001"

    objects = BaseModelManager.from_queryset(PostingQuerySet)()

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
    deleted = models.BooleanField(default=False)

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

    crossover_carrier = models.CharField(max_length=255, null=True, blank=True)
    crossover_id = models.CharField(max_length=255, null=True, blank=True)
    payer_icn = models.CharField(max_length=255, null=True, blank=True)
    position_in_era = models.PositiveIntegerField(null=True, blank=True)


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
            return Decimal(0)

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


class AbstractBulkPosting(TimestampedModel, IdentifiableModel):
    """Patient and Insurance bulk posting shared columns."""

    class Meta:
        abstract = True

    objects = BaseModelManager()

    payment_collection = models.OneToOneField(
        "v1.PaymentCollection", related_name="%(class)s", on_delete=models.PROTECT
    )
    deleted = models.BooleanField(default=False)

    total_paid = models.DecimalField(max_digits=8, decimal_places=2)


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

    # Claims a remit covers, including claims whose remit processing was skipped.
    claims = models.ManyToManyField(
        "v1.Claim", related_name="remits", through="v1.BaseRemittanceAdviceClaim"
    )

    era_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)

    @property
    def total_posted_amount(self) -> Decimal:
        """Property to compute how much was posted with all associated postings."""
        postings = self.postings.active()
        return quantize(sum(posting.posted_amount for posting in postings))


class BaseRemittanceAdviceClaim(Model):
    """M2M for BaseRemittanceAdvice -> Claims."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_remittanceadvice_claims_001"

    remittance = models.ForeignKey(
        BaseRemittanceAdvice, on_delete=models.CASCADE, db_column="baseremittanceadvice_id"
    )
    claim = models.ForeignKey("v1.Claim", on_delete=models.CASCADE)


class ManualRemittanceAdvice(BaseRemittanceAdvice):
    """A remit posted by hand."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_manualremittanceadvice_001"


class ElectronicRemittanceAdvice(BaseRemittanceAdvice):
    """An electronic remit (ERA)."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_electronicremittance_001"

    check_type = models.CharField(max_length=25, null=True, blank=True)
    provider_name = models.CharField(max_length=255, null=True, blank=True)
    payer_name = models.CharField(max_length=255, null=True, blank=True)
    download_date = models.DateField(null=True, blank=True)
    provider_npi = models.CharField(max_length=255, null=True, blank=True)
    received_time = models.DateTimeField(null=True, blank=True)


class NewRemittanceDocument(TimestampedModel):
    """The file a manual or electronic remit was posted from."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_newremittancedocument_001"

    objects = cast(CommittableQuerySet, CommittableModelManager())

    originator = models.ForeignKey("v1.CanvasUser", on_delete=models.PROTECT, related_name="+")
    committer = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.PROTECT, related_name="+", null=True
    )
    entered_in_error = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.PROTECT, related_name="+", null=True
    )
    deleted = models.BooleanField(default=False)

    remittance = models.OneToOneField(
        BaseRemittanceAdvice, related_name="document", on_delete=models.PROTECT
    )
    document = models.FileField(max_length=100)

    @property
    def document_url(self) -> str | None:
        """Return a presigned URL for the remit file, or None if unset."""
        if self.document:
            return presigned_url(self.document.name)
        return None


__exports__ = (
    "BasePosting",
    "CoveragePosting",
    "PatientPosting",
    "BulkPatientPosting",
    "BaseRemittanceAdvice",
    "BaseRemittanceAdviceClaim",
    "ManualRemittanceAdvice",
    "ElectronicRemittanceAdvice",
    "NewRemittanceDocument",
)
