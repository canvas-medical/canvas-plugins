from django.db import models

from canvas_sdk.v1.data.common import TaxIDType


class Organization(models.Model):
    """Organization."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_organization_001"

    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    full_name = models.CharField()
    short_name = models.CharField()
    subdomain = models.CharField()
    logo_url = models.CharField()
    background_image_url = models.CharField()
    background_gradient = models.CharField()
    active = models.BooleanField()
    tax_id = models.CharField(null=True)
    tax_id_type = models.CharField(choices=TaxIDType.choices)
    group_npi_number = models.CharField()
    group_taxonomy_number = models.CharField()
    include_zz_qualifier = models.BooleanField()
    main_location = models.OneToOneField("v1.PracticeLocation", on_delete=models.DO_NOTHING)


__exports__ = ("Organization",)
