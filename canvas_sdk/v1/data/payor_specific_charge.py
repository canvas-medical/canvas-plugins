from django.db import models


class PayorSpecificCharge(models.Model):
    """Payor Specific Charge."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_quality_and_revenue_payorspecificcharge_001"

    dbid = models.BigIntegerField(primary_key=True)
    transactor = models.ForeignKey(
        "v1.Transactor", related_name="specific_charges", on_delete=models.DO_NOTHING
    )
    # uncomment this when ChargeDescriptionMaster is added to data module
    # charge = models.ForeignKey(
    #     "v1.ChargeDescriptionMaster",
    #     related_name="transactor_charges",
    #     on_delete=models.DO_NOTHING,
    # )

    charge_amount = models.DecimalField()
    effective_date = models.DateField()
    end_date = models.DateField()
    part_of_capitated_set = models.BooleanField()


__exports__ = ("PayorSpecificCharge",)
