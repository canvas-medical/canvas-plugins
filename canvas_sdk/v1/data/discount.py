from django.db import models

from canvas_sdk.v1.data.base import Model


class Discount(Model):
    """Model to represent a discount applied to a claim or patient posting."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_discount_001"

    name = models.CharField(max_length=500)
    adjustment_group = models.CharField(max_length=3)
    adjustment_code = models.CharField(max_length=3)
    discount = models.DecimalField(max_digits=8, decimal_places=2)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


__exports__ = ("Discount",)
