from django.db import models


class CDMCodeSystem(models.TextChoices):
    """CDMCodeSystem."""

    INTERNAL = "INTERNAL", "Internal"
    CPT = "CPT", "CPT"


class ChargeDescriptionMaster(models.Model):
    """Charge Description Master."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_quality_and_revenue_chargedescriptionmaster_001"

    dbid = models.BigIntegerField(primary_key=True)
    cpt_code = models.CharField()
    name = models.CharField()
    short_name = models.CharField()
    charge_amount = models.DecimalField()
    effective_date = models.DateField()
    end_date = models.DateField()
    code_system = models.CharField(choices=CDMCodeSystem.choices)
    ndc_code = models.CharField()


__exports__ = ("ChargeDescriptionMaster",)
