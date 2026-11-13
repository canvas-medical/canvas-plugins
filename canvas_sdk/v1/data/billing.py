from typing import TYPE_CHECKING, Self

from django.db import models

from canvas_sdk.v1.data.base import (
    IdentifiableModel,
    TimestampedModel,
    ValueSetTimeframeLookupQuerySet,
)
from canvas_sdk.v1.data.coding import Coding
from canvas_sdk.value_set.value_set import CodeConstants

if TYPE_CHECKING:
    from canvas_sdk.value_set.value_set import ValueSet


# The value set code systems whose codes a billing line item's `cpt` field can hold.
BILLING_CODE_SYSTEMS = (CodeConstants.CPT, CodeConstants.HCPCSLEVELII, CodeConstants.HCPCS)


class BillingLineItemQuerySet(ValueSetTimeframeLookupQuerySet):
    """A class that adds functionality to filter BillingLineItem objects."""

    def find(self, value_set: type["ValueSet"]) -> Self:
        """
        Billing line items whose code is in the value set's CPT or HCPCS codes.

        A line item stores its code as a plain string in the `cpt` field, with no code
        system, so codes from the value set's CPT, HCPCSLEVELII, and HCPCS systems all match.
        """
        values = value_set.values
        codes: set[str] = set()
        for system in BILLING_CODE_SYSTEMS:
            codes |= values.get(system, set())
        return self.filter(cpt__in=codes)


class BillingLineItemStatus(models.TextChoices):
    """Billing line item status."""

    ACTIVE = "active", "Active"
    REMOVED = "removed", "Removed"


class BillingLineItem(TimestampedModel, IdentifiableModel):
    """BillingLineItem."""

    class Meta:
        db_table = "canvas_sdk_data_api_billinglineitem_001"

    objects = models.Manager().from_queryset(BillingLineItemQuerySet)()

    note = models.ForeignKey(
        "v1.Note",
        on_delete=models.DO_NOTHING,
        related_name="billing_line_items",
        null=True,
    )
    patient = models.ForeignKey(
        "v1.Patient",
        on_delete=models.DO_NOTHING,
        related_name="billing_line_items",
        null=True,
    )
    cpt = models.CharField(max_length=10)
    charge = models.DecimalField(decimal_places=2, max_digits=8)
    description = models.CharField(max_length=255)
    units = models.IntegerField()
    command_type = models.CharField(max_length=50)
    command_id = models.IntegerField()
    status = models.CharField(choices=BillingLineItemStatus.choices, max_length=20)
    assessments = models.ManyToManyField(
        "v1.Assessment",
        related_name="billinglineitem_set",
        db_table="canvas_sdk_data_api_billinglineitem_assessments_001",
    )


class BillingLineItemModifier(Coding):
    """BillingLineItemModifier."""

    class Meta:
        db_table = "canvas_sdk_data_api_billinglineitemmodifier_001"

    line_item = models.ForeignKey(
        "v1.BillingLineItem",
        on_delete=models.DO_NOTHING,
        related_name="modifiers",
        null=True,
    )


__exports__ = (
    "BillingLineItemStatus",
    "BillingLineItem",
    "BillingLineItemModifier",
)
