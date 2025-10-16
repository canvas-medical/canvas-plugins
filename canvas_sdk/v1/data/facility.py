from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel


class Facility(IdentifiableModel):
    """Facility model representing a healthcare facility."""

    class Meta:
        db_table = "canvas_sdk_data_api_facility_001"

    name = models.CharField(max_length=255)
    npi_number = models.CharField(verbose_name="NPI number", max_length=10, blank=True)
    phone_number = models.CharField(max_length=10, blank=True, default="")
    fax_number = models.CharField(max_length=10, blank=True, default="")
    active = models.BooleanField(default=True)
    line1 = models.CharField(max_length=255, default="", blank=True)
    line2 = models.CharField(max_length=255, default="", blank=True)
    city = models.CharField(max_length=255)
    district = models.CharField(max_length=255, blank=True, default="")
    state_code = models.CharField(max_length=2)
    postal_code = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


__exports__ = ("Facility",)
