from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel


class POCLabTemplate(TimestampedModel, IdentifiableModel):
    """A Point of Care lab template — mirrors data_integration.POCLabTemplateProxy."""

    class Meta:
        db_table = "canvas_sdk_data_data_integration_poclabtemplate_001"

    name = models.CharField(max_length=255)
    loinc_code = models.CharField(max_length=32, blank=True, default="")
    loinc_display = models.CharField(max_length=255, blank=True, default="")
    active = models.BooleanField(default=True)


__exports__ = ("POCLabTemplate",)
