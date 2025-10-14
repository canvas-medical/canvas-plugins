import factory

from canvas_sdk.v1.data import PracticeLocation, PracticeLocationSetting


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
