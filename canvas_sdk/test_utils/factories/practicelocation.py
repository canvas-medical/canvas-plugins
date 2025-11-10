from datetime import date

import factory

from canvas_sdk.v1.data import PracticeLocation, PracticeLocationAddress, PracticeLocationSetting
from canvas_sdk.v1.data.common import AddressState, AddressType, AddressUse


class PracticeLocationSettingFactory(factory.django.DjangoModelFactory[PracticeLocationSetting]):
    """Factory for PracticeLocationSetting."""

    class Meta:
        model = PracticeLocationSetting
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"location_setting_{n}")
    value = {"random": "json"}


class PracticeLocationFactory(factory.django.DjangoModelFactory[PracticeLocation]):
    """Factory for PracticeLocation."""

    class Meta:
        model = PracticeLocation

    organization = factory.SubFactory(
        "canvas_sdk.test_utils.factories.organization.OrganizationFactory"
    )
    short_name = "Family Doctors of SF"
    full_name = "Family Doctors of San Francisco"
    setting = factory.RelatedFactory(PracticeLocationSettingFactory, "practice_location")
    bill_through_organization = True
    billing_location_name = "Billing Location Name"
    tax_id = "123456789"
    tax_id_type = "E"
    npi_number = "1234567890"
    group_npi_number = "112233445"


class PracticeLocationAddressFactory(factory.django.DjangoModelFactory[PracticeLocationAddress]):
    """Factory for PracticeLocationAddress."""

    class Meta:
        model = PracticeLocationAddress

    practice_location = factory.SubFactory(
        "canvas_sdk.test_utils.factories.PracticeLocationFactory"
    )
    line1 = "1234 Golden Gate Ave."
    line2 = "Suite 456"
    city = "San Francisco"
    district = ""
    state_code = "CA"
    postal_code = "94100"
    use = AddressUse.WORK
    type = AddressType.BOTH
    longitude = -122.476944
    latitude = 37.769722
    start = date(year=2015, month=10, day=10)
    end = None
    country = "USA"
    state = AddressState.ACTIVE
