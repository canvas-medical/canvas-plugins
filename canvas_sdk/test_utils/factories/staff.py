import datetime

import factory
from dateutil.relativedelta import relativedelta

from canvas_sdk.v1.data import (
    Staff,
    StaffAddress,
    StaffContactPoint,
    StaffLicense,
    StaffPhoto,
    StaffRole,
)
from canvas_sdk.v1.data.common import ContactPointSystem, ContactPointUse


class StaffAddressFactory(factory.django.DjangoModelFactory[StaffAddress]):
    """Factory for creating StaffAddress."""

    class Meta:
        model = StaffAddress

    line1 = "1234 Main Street"
    line2 = "Apt 3"
    city = "San Francisco"
    district = "Sunset"
    state_code = "CA"
    postal_code = "94112"
    country = "USA"
    staff = factory.SubFactory("canvas_sdk.test_utils.factories.StaffFactory")


class StaffPhotoFactory(factory.django.DjangoModelFactory[StaffPhoto]):
    """Factory for creating StaffPhoto."""

    class Meta:
        model = StaffPhoto

    url = ""
    staff = factory.SubFactory("canvas_sdk.test_utils.factories.StaffFactory")


class StaffRoleFactory(factory.django.DjangoModelFactory[StaffRole]):
    """Factory for creating StaffRole."""

    class Meta:
        model = StaffRole
        django_get_or_create = ("internal_code", "staff")

    internal_code = "MD"
    name = "Physician"
    public_abbreviation = "MD"
    domain = StaffRole.RoleDomain.CLINICAL
    domain_privilege_level = 100000
    permissions = factory.LazyFunction(lambda: {})
    staff = factory.SubFactory("canvas_sdk.test_utils.factories.StaffFactory")


class StaffLicenseFactory(factory.django.DjangoModelFactory[StaffLicense]):
    """Factory for creating StaffLicense."""

    class Meta:
        model = StaffLicense

    issuing_authority_long_name = "MEDICAL BOARD OF CALIFORNIA"
    issuing_authority_url = "http://www.mbc.ca.gov/"
    license_or_certification_identifier = "A60695"
    issuance_date = factory.LazyFunction(datetime.date.today)
    expiration_date = factory.LazyFunction(lambda: datetime.date.today() + relativedelta(years=2))
    staff = factory.SubFactory("canvas_sdk.test_utils.factories.StaffFactory")


class StaffContactPointFactory(factory.django.DjangoModelFactory[StaffContactPoint]):
    """Factory for creating StaffContactPoint."""

    class Meta:
        model = StaffContactPoint

    value = "8883331212"
    system = ContactPointSystem.PHONE
    use = ContactPointUse.HOME
    staff = factory.SubFactory("canvas_sdk.test_utils.factories.StaffFactory")


class StaffFactory(factory.django.DjangoModelFactory[Staff]):
    """Factory for creating Staff."""

    class Meta:
        model = Staff
        django_get_or_create = ("user",)

    first_name = factory.Faker("first_name")
    middle_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    npi_number = "1111155556"
    group_npi_number = "123456789"
    tax_id = "98711111"
    spi_number = 5630156655001
    address = factory.RelatedFactory(StaffAddressFactory, "staff")
    telecom = factory.RelatedFactory(StaffContactPointFactory, "staff")
    primary_practice_location = factory.SubFactory(
        "canvas_sdk.test_utils.factories.PracticeLocationFactory"
    )
    photos = factory.RelatedFactory(StaffPhotoFactory, "staff")
    role = factory.RelatedFactory(StaffRoleFactory, "staff")
    license = factory.RelatedFactory(StaffLicenseFactory, "staff")
    birth_date = factory.Faker("date_object")

    user = factory.SubFactory(
        "canvas_sdk.test_utils.factories.user.CanvasUserFactory",
    )
