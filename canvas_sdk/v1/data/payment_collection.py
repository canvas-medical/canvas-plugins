from django.db import models


class PostingMethods(models.TextChoices):
    """PostingMethods."""

    CASH = "cash", "Cash"
    CHECK = "check", "Check"
    CARD = "card", "Card"
    OTHER = "other", "Other"


class PaymentCollection(models.Model):
    """Stores the total collected amount and the payment method."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_quality_and_revenue_paymentcollection_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    total_collected = models.DecimalField(max_digits=8, decimal_places=2)
    method = models.CharField(choices=PostingMethods.choices)

    check_number = models.CharField()
    check_date = models.DateField()
    deposit_date = models.DateField()

    description = models.TextField()

    created = models.DateTimeField()
    modified = models.DateTimeField()


__exports__ = ("PaymentCollection", "PostingMethods")
