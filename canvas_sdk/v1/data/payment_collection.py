from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel


class PostingMethods(models.TextChoices):
    """PostingMethods."""

    CASH = "cash", "Cash"
    CHECK = "check", "Check"
    CARD = "card", "Card"
    OTHER = "other", "Other"


class PaymentCollection(IdentifiableModel):
    """Stores the total collected amount and the payment method."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_paymentcollection_001"

    total_collected = models.DecimalField(max_digits=8, decimal_places=2)
    method = models.CharField(choices=PostingMethods.choices, max_length=10)

    check_number = models.CharField(max_length=250)
    check_date = models.DateField()
    deposit_date = models.DateField()

    description = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


__exports__ = ("PaymentCollection", "PostingMethods")
