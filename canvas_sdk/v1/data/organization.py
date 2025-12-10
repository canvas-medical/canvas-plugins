from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel
from canvas_sdk.v1.data.common import (
    AddressState,
    AddressType,
    AddressUseWithBilling,
    ContactPointState,
    ContactPointSystem,
    ContactPointUse,
    TaxIDType,
)


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


class OrganizationAddress(IdentifiableModel):
    """Organization Address."""

    class Meta:
        db_table = "canvas_sdk_data_api_organizationaddress_001"

    organization = models.ForeignKey(
        "v1.Organization", on_delete=models.PROTECT, related_name="addresses"
    )
    use = models.CharField(
        choices=AddressUseWithBilling.choices, max_length=10, default=AddressUseWithBilling.HOME
    )
    type = models.CharField(choices=AddressType.choices, max_length=10, default=AddressType.BOTH)
    longitude = models.FloatField(null=True, default=None, blank=True)
    latitude = models.FloatField(null=True, default=None, blank=True)
    start = models.DateField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=255)
    state = models.CharField(
        choices=AddressState.choices, max_length=20, default=AddressState.ACTIVE
    )
    address_search_index = models.TextField(default="", null=True, blank=True)
    line1 = models.CharField(max_length=255, default="", blank=True)
    line2 = models.CharField(max_length=255, default="", blank=True)
    city = models.CharField(max_length=255)
    district = models.CharField(max_length=255, blank=True, default="")
    state_code = models.CharField(max_length=2)
    postal_code = models.CharField(max_length=255)


class OrganizationContactPoint(IdentifiableModel):
    """OrganizationContactPoint."""

    class Meta:
        db_table = "canvas_sdk_data_api_organizationcontactpoint_001"

    organization = models.ForeignKey(
        "v1.Organization", on_delete=models.PROTECT, related_name="telecom"
    )
    system = models.CharField(choices=ContactPointSystem.choices, max_length=20, db_index=True)
    value = models.CharField(max_length=100, db_index=True)
    use = models.CharField(
        choices=ContactPointUse.choices, max_length=20, default=ContactPointUse.HOME
    )
    use_notes = models.CharField(max_length=255, blank=True, default="")
    rank = models.IntegerField(default=1)
    state = models.CharField(
        choices=ContactPointState.choices, max_length=20, default=ContactPointState.ACTIVE
    )


__exports__ = (
    "Organization",
    "OrganizationAddress",
    "OrganizationContactPoint",
)
