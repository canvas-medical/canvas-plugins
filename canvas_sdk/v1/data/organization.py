from django.db import models

from canvas_sdk.v1.data.base import TimestampedModel
from canvas_sdk.v1.data.common import TaxIDType


class Organization(TimestampedModel):
    """Organization."""

    class Meta:
        db_table = "canvas_sdk_data_api_organization_001"

    full_name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=255)
    subdomain = models.CharField(max_length=100)
    logo_url = models.CharField(max_length=255)
    background_image_url = models.CharField(max_length=255)
    background_gradient = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    tax_id = models.CharField(null=True, max_length=25)
    tax_id_type = models.CharField(choices=TaxIDType.choices, max_length=1)
    group_npi_number = models.CharField(max_length=10)
    group_taxonomy_number = models.CharField(max_length=10)
    include_zz_qualifier = models.BooleanField(default=False)
    main_location = models.OneToOneField(
        "PracticeLocation", related_name="+", null=True, on_delete=models.PROTECT
    )


__exports__ = ("Organization",)
