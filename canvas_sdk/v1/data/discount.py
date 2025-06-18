from django.db import models


class Discount(models.Model):
    """Model to represent a discount applied to a claim or patient posting."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_quality_and_revenue_discount_001"

    dbid = models.BigIntegerField(primary_key=True)
    name = models.CharField()
    adjustment_group = models.CharField()
    adjustment_code = models.CharField()
    discount = models.DecimalField(max_digits=8, decimal_places=2)

    created = models.DateTimeField()
    modified = models.DateTimeField()


__exports__ = ("Discount",)
