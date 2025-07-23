from django.db import models

from canvas_sdk.v1.data.base import Model


class CDMCodeSystem(models.TextChoices):
    """CDMCodeSystem."""

    INTERNAL = "INTERNAL", "Internal"
    CPT = "CPT", "CPT"


class ChargeDescriptionMaster(Model):
    """Charge Description Master."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_chargedescriptionmaster_001"

    cpt_code = models.CharField(max_length=10)
    name = models.CharField(max_length=17000)
    short_name = models.CharField(max_length=17000)
    charge_amount = models.DecimalField(max_digits=8, decimal_places=2)
    effective_date = models.DateField()
    end_date = models.DateField(null=True)
    code_system = models.CharField(choices=CDMCodeSystem.choices, max_length=10)
    ndc_code = models.CharField(max_length=255)


__exports__ = ("ChargeDescriptionMaster",)
