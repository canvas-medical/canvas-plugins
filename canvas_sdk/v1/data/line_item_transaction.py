from django.db import models
from django.db.models import QuerySet

from canvas_sdk.v1.data.base import Model


class AbstractLineItemQuerySet(models.QuerySet):
    """AbstractLineItemQuerySet."""

    def active(self) -> QuerySet:
        """Filter out line items that have been entered in error."""
        return self.filter(entered_in_error__isnull=True)


class AbstractLineItemTransaction(Model):
    """Abstract class with common properties for both payments and adjustments."""

    class Meta:
        abstract = True

    objects = AbstractLineItemQuerySet.as_manager()

    posting = models.ForeignKey(
        "v1.BasePosting", related_name="%(class)ss", on_delete=models.PROTECT
    )
    billing_line_item = models.ForeignKey(
        "v1.BillingLineItem", related_name="%(class)ss", on_delete=models.PROTECT
    )
    amount = models.DecimalField(max_digits=8, decimal_places=2)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class NewLineItemPayment(AbstractLineItemTransaction):
    """Subclass that represents a payment on a billing line item."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_newlineitempayment_001"

    charged = models.DecimalField(max_digits=8, decimal_places=2)


class AbstractLineItemAdjustment(AbstractLineItemTransaction):
    """Abstract subclass with common fields for both adjustment and transfer."""

    class Meta:
        abstract = True

    code = models.CharField(max_length=8)
    group = models.CharField(max_length=8)

    deviated_from_posting_ruleset = models.BooleanField()


class NewLineItemAdjustment(AbstractLineItemAdjustment):
    """Subclass for billing line item adjustments."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_newlineitemadjustment_001"

    write_off = models.BooleanField()


class LineItemTransfer(AbstractLineItemAdjustment):
    """Subclass for billing line item balance transfer to other coverages or patient."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_lineitemtransfer_001"

    transfer_to = models.ForeignKey(
        "v1.ClaimCoverage", related_name="transfers", on_delete=models.PROTECT, null=True
    )
    transfer_to_patient = models.BooleanField(default=False)


__exports__ = (
    "NewLineItemPayment",
    "NewLineItemAdjustment",
    "LineItemTransfer",
)
