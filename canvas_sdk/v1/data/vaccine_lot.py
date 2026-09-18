from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel


class VaccineCatalog(TimestampedModel, IdentifiableModel):
    """A vaccine catalog entry (name + CVX coding)."""

    class Meta:
        db_table = "canvas_sdk_data_api_vaccinecatalog_001"

    name = models.CharField(max_length=255)
    cvx_code = models.CharField(max_length=16)
    cvx_display = models.CharField(max_length=255, blank=True, default="")
    manufacturer = models.CharField(max_length=255, blank=True, default="")
    active = models.BooleanField(default=True)


__exports__ = ("VaccineCatalog",)
