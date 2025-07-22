from typing import TYPE_CHECKING, Self

from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, Model, ValueSetTimeframeLookupQuerySet
from canvas_sdk.value_set.value_set import CodeConstants

if TYPE_CHECKING:
    from canvas_sdk.value_set.value_set import ValueSet


class BillingLineItemQuerySet(ValueSetTimeframeLookupQuerySet):
    """A class that adds functionality to filter BillingLineItem objects."""

    def find(self, value_set: type["ValueSet"]) -> Self:
        """
        This method is overridden to use for BillingLineItem CPT codes.
        The codes are saved as string values in the BillingLineItem.cpt field,
        which differs from other coding models.
        """
        values_dict = value_set.values
        return self.filter(cpt__in=values_dict.get(CodeConstants.HCPCS, []))


class BillingLineItemStatus(models.TextChoices):
    """Billing line item status."""

    ACTIVE = "active", "Active"
    REMOVED = "removed", "Removed"


class BillingLineItem(IdentifiableModel):
    """BillingLineItem."""

    class Meta:
        db_table = "canvas_sdk_data_api_billinglineitem_001"

    # objects = BillingLineItemQuerySet.as_manager()
    objects = models.Manager().from_queryset(BillingLineItemQuerySet)()

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
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


class BillingLineItemModifier(Model):
    """BillingLineItemModifier."""

    class Meta:
        db_table = "canvas_sdk_data_api_billinglineitemmodifier_001"

    system = models.CharField(max_length=255)
    version = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    display = models.CharField(max_length=1000)
    user_selected = models.BooleanField()
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
