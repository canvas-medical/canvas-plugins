from django.db import models

from canvas_sdk.v1.data.base import Model


class PayorSpecificCharge(Model):
    """Payor Specific Charge."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_payorspecificcharge_001"

    transactor = models.ForeignKey(
        "v1.Transactor", related_name="specific_charges", on_delete=models.DO_NOTHING
    )
    charge = models.ForeignKey(
        "v1.ChargeDescriptionMaster",
        related_name="transactor_charges",
        on_delete=models.DO_NOTHING,
    )
    charge_amount = models.DecimalField(max_digits=8, decimal_places=2)
    effective_date = models.DateField()
    end_date = models.DateField(null=True)
    part_of_capitated_set = models.BooleanField()


__exports__ = ("PayorSpecificCharge",)
