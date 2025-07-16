from decimal import Decimal
from typing import Any, Self

from django.db import models
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce

from canvas_sdk.v1.data.base import Model
from canvas_sdk.v1.data.note import PracticeLocationPOS


class ClaimLineItemStatus(models.TextChoices):
    """ClaimLineItemStatus."""

    ACTIVE = "active", "Active"
    REMOVED = "removed", "Removed"


class LineItemCodes(models.TextChoices):
    """LineItemCodes."""

    COPAY = "COPAY"
    UNLINKED = "UNLINKED"


class FamilyPlanningOptions(models.TextChoices):
    """FamilyPlanningOptions."""

    YES = ("Y", "Yes")
    NO = ("N", "No")


class ClaimLineItemQuerySet(models.QuerySet):
    """ClaimLineItemQuerySet."""

    def filter(self, *args: Any, **kwargs: Any) -> Self:
        """Apply standard filtering to the QuerySet."""
        return super().filter(*args, **kwargs)

    def exclude(self, *args: Any, **kwargs: Any) -> Self:
        """Apply standard exclusion to the QuerySet."""
        return super().exclude(*args, **kwargs)

    def apply_ordering(self) -> Self:
        """Apply ordering to the QuerySet."""
        return self.order_by("from_date", "-proc_code")

    def active(self) -> Self:
        """Return only active claim line items."""
        return self.exclude(status=ClaimLineItemStatus.REMOVED).apply_ordering()

    def exclude_removed_line_item_without_active_posting(self) -> Self:
        """Exclude out any line items that are deleted without any active postings."""
        return (
            self.filter(
                Q(status=ClaimLineItemStatus.ACTIVE)
                | Q(
                    newlineitempayments__isnull=False,
                    newlineitempayments__entered_in_error__isnull=True,
                )
                | Q(
                    newlineitemadjustments__isnull=False,
                    newlineitemadjustments__entered_in_error__isnull=True,
                )
                | Q(
                    lineitemtransfers__isnull=False,
                    lineitemtransfers__entered_in_error__isnull=True,
                )
            )
            .exclude_removed_line_items_without_balances()
            .apply_ordering()
            .distinct()
        )

    def exclude_removed_line_items_without_balances(self) -> Self:
        """Exclude removed line items with zero balances."""
        return (
            self.annotate(
                sum_of_all_payments=Coalesce(Sum("newlineitempayments__amount"), Decimal(0)),
                sum_of_all_adjustments=Coalesce(Sum("newlineitemadjustments__amount"), Decimal(0)),
                sum_of_all_transfers=Coalesce(Sum("lineitemtransfers__amount"), Decimal(0)),
            )
            .exclude(
                Q(
                    status=ClaimLineItemStatus.REMOVED,
                    sum_of_all_payments=0,
                    sum_of_all_adjustments=0,
                    sum_of_all_transfers=0,
                )
            )
            .distinct()
        )

    def exclude_copay_and_unlinked(self) -> Self:
        """Exclude both co-pay and unlinked line items."""
        return self.exclude(
            proc_code__in=[LineItemCodes.UNLINKED.value, LineItemCodes.COPAY.value]
        ).apply_ordering()

    def exclude_copay(self) -> Self:
        """Exclude only co-pay line items."""
        return self.exclude(proc_code=LineItemCodes.COPAY.value).apply_ordering()

    def exclude_unlinked(self) -> Self:
        """Exclude only unlinked line items."""
        return self.exclude(proc_code=LineItemCodes.UNLINKED.value).apply_ordering()


class ClaimLineItem(Model):
    """ClaimLineItem."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_claimlineitem_001"

    objects = ClaimLineItemQuerySet.as_manager()

    billing_line_item = models.ForeignKey("v1.BillingLineItem", on_delete=models.CASCADE, null=True)
    claim = models.ForeignKey("v1.Claim", on_delete=models.CASCADE, related_name="line_items")
    status = models.CharField(choices=ClaimLineItemStatus.choices, max_length=10)
    charge = models.DecimalField(max_digits=8, decimal_places=2)
    from_date = models.CharField(max_length=10)
    thru_date = models.CharField(max_length=10)
    narrative = models.CharField(max_length=2000)
    ndc_code = models.CharField(max_length=100)
    ndc_dosage = models.CharField(max_length=100)
    ndc_measure = models.CharField(max_length=100)
    place_of_service = models.CharField(choices=PracticeLocationPOS.choices, max_length=2)
    proc_code = models.CharField(max_length=10)
    display = models.CharField(max_length=255)
    remote_chg_id = models.CharField(max_length=100)
    units = models.IntegerField()
    epsdt = models.CharField(max_length=2)
    family_planning = models.CharField(choices=FamilyPlanningOptions.choices, max_length=1)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


__exports__ = ("ClaimLineItem", "ClaimLineItemStatus", "LineItemCodes", "FamilyPlanningOptions")
