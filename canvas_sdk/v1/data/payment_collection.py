from django.contrib.postgres.fields import ArrayField
from django.db import models

from canvas_sdk.v1.data.base import (
    AuditedModel,
    BaseModelManager,
    IdentifiableModel,
    TimestampedModel,
)


class PostingMethods(models.TextChoices):
    """PostingMethods."""

    CASH = "cash", "Cash"
    CHECK = "check", "Check"
    CARD = "card", "Card"
    OTHER = "other", "Other"


class PaymentCollection(TimestampedModel, IdentifiableModel):
    """Stores the total collected amount and the payment method."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_paymentcollection_001"

    objects = BaseModelManager()

    deleted = models.BooleanField(default=False)

    total_collected = models.DecimalField(max_digits=8, decimal_places=2)
    method = models.CharField(choices=PostingMethods.choices, max_length=10)

    check_number = models.CharField(max_length=250, null=True, blank=True)
    check_date = models.DateField(null=True)
    deposit_date = models.DateField(null=True)

    description = models.TextField()


class CreditCardChargeState(models.TextChoices):
    """CreditCardChargeState."""

    PENDING = "Pending", "Pending"
    CHARGED = "Charged", "Charged"
    SUCCESSFUL = "Successful", "Successful"
    FAILED = "Failed", "Failed"


class CreditCardCharge(AuditedModel, IdentifiableModel):
    """A card charge made through a payment provider for a payment collection."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_creditcardcharge_001"

    objects = BaseModelManager()

    # Every charge has an originator, unlike the optional one on AuditedModel.
    originator = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, related_name="+")
    editors = ArrayField(models.IntegerField(), null=True, blank=True)
    payment_collection = models.ForeignKey(
        PaymentCollection, on_delete=models.DO_NOTHING, related_name="credit_card_charges"
    )
    payment_method = models.ForeignKey(
        "v1.PaymentCard",
        on_delete=models.DO_NOTHING,
        related_name="credit_card_charges",
        null=True,
    )
    state = models.CharField(
        max_length=50, choices=CreditCardChargeState.choices, default=CreditCardChargeState.PENDING
    )
    provider = models.CharField(max_length=255, default="stripe")


__exports__ = (
    "CreditCardCharge",
    "CreditCardChargeState",
    "PaymentCollection",
    "PostingMethods",
)
