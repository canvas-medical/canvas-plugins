from typing import TYPE_CHECKING, Type

from django.db import models

from canvas_sdk.v1.data.base import ValueSetTimeframeLookupQuerySet
from canvas_sdk.v1.data.note import Note
from canvas_sdk.v1.data.patient import Patient
from canvas_sdk.value_set.value_set import CodeConstants

if TYPE_CHECKING:
    from canvas_sdk.value_set.value_set import ValueSet


class BillingLineItemQuerySet(ValueSetTimeframeLookupQuerySet):
    """A class that adds functionality to filter BillingLineItem objects."""

    def find(self, value_set: Type["ValueSet"]) -> models.QuerySet:
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


class BillingLineItem(models.Model):
    """BillingLineItem."""

    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_billinglineitem_001"

    # objects = BillingLineItemQuerySet.as_manager()
    objects = models.Manager().from_queryset(BillingLineItemQuerySet)()

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    note = models.ForeignKey(Note, on_delete=models.DO_NOTHING, related_name="billing_line_items")
    patient = models.ForeignKey(
        Patient, on_delete=models.DO_NOTHING, related_name="billing_line_items"
    )
    cpt = models.CharField()
    charge = models.DecimalField()
    description = models.CharField()
    units = models.IntegerField()
    command_type = models.CharField()
    command_id = models.IntegerField()
    status = models.CharField(choices=BillingLineItemStatus.choices)
