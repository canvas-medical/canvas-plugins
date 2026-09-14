from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel


class PaymentCard(TimestampedModel, IdentifiableModel):
    """A patient's stored payment card on file."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_paymentmethod_001"

    patient = models.ForeignKey(
        "v1.Patient",
        on_delete=models.DO_NOTHING,
        related_name="payment_cards",
        null=True,
    )
    card_last_four_digits = models.CharField(max_length=4)
    brand = models.CharField(max_length=50)
    expiration_month = models.CharField(max_length=2)
    expiration_year = models.CharField(max_length=4)
    card_holder_name = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=32)
    is_default = models.BooleanField(default=False)


__exports__ = ("PaymentCard",)
