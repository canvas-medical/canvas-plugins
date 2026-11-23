from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel


class InpatientFacility(IdentifiableModel):
    """A facility where a patient is admitted for an inpatient stay."""

    class Meta:
        db_table = "canvas_sdk_data_api_inpatientfacility_001"

    name = models.CharField(max_length=64)
    npi_number = models.CharField(max_length=10)
    line1 = models.CharField(max_length=64, blank=True, default="")
    line2 = models.CharField(max_length=64, blank=True, default="")
    city = models.CharField(max_length=64, blank=True, default="")
    state_code = models.CharField(max_length=2, blank=True, default="")
    postal_code = models.CharField(max_length=64, blank=True, default="")


class InpatientStay(IdentifiableModel):
    """A patient's admission to an inpatient facility, which rounding notes are written against."""

    class Meta:
        db_table = "canvas_sdk_data_api_inpatientstay_001"

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="inpatient_stays"
    )
    inpatient_facility = models.ForeignKey(
        "v1.InpatientFacility",
        on_delete=models.DO_NOTHING,
        related_name="inpatient_stays",
        null=True,
    )
    room_number = models.CharField(max_length=32, blank=True, default="")
    external_mrn = models.CharField(max_length=32, blank=True, default="")
    referring_provider = models.CharField(max_length=250, blank=True, default="")
    admit_time = models.DateTimeField(null=True)
    discharge_time = models.DateTimeField(null=True)


__exports__ = (
    "InpatientFacility",
    "InpatientStay",
)
