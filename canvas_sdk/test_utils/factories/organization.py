import factory

from canvas_sdk.v1.data import (
    Organization,
    OrganizationAddress,
    OrganizationContactPoint,
    OrganizationSetting,
)
from canvas_sdk.v1.data.common import ContactPointSystem, ContactPointUse


class OrganizationFactory(factory.django.DjangoModelFactory[Organization]):
    """Factory for creating Organization."""

    class Meta:
        model = Organization

    short_name = "Canvas Medical"
    full_name = "Canvas Medical, Inc."
    logo_url = "https://s3-us-west-2.amazonaws.com/canvas-pcp-assets/canvas_logo_large.png"
    background_image_url = "https://s3-us-west-2.amazonaws.com/canvas-pcp-assets/santa-cruz-low.jpg"
    background_gradient = (
        "linear-gradient(to top, rgb(231, 201, 154) 0%, rgb(220, 210, 192) 29%, "
        "rgb(156, 175, 191) 90%, rgb(147, 166, 189) 100%)"
    )
    tax_id = "123456"


class OrganizationAddressFactory(factory.django.DjangoModelFactory[OrganizationAddress]):
    """Factory for creating OrganizationAddress."""

    class Meta:
        model = OrganizationAddress

    organization = factory.SubFactory(OrganizationFactory)
    line1 = "456 Organization Ave"
    line2 = "#2"
    city = "San Francisco"
    district = "Sunset"
    state_code = "CA"
    postal_code = "94112"
    country = "USA"


class OrganizationContactPointFactory(factory.django.DjangoModelFactory[OrganizationContactPoint]):
    """Factory for creating OrganizationContactPoint."""

    class Meta:
        model = OrganizationContactPoint

    organization = factory.SubFactory(OrganizationFactory)
    system = ContactPointSystem.PHONE
    value = "8003701416"
    use = ContactPointUse.WORK
    rank = 1


class OrganizationSettingFactory(factory.django.DjangoModelFactory[OrganizationSetting]):
    """Factory for creating an OrganizationSetting, by default the appointment reminder schedule.

    Setting names are unique, so creating a name that already exists returns the existing row
    and ignores the other arguments; update that row to change its value.
    """

    class Meta:
        model = OrganizationSetting
        django_get_or_create = ("name",)

    organization = factory.SubFactory(OrganizationFactory)
    name = "appointmentReminders"
    value = factory.LazyFunction(lambda: {"daysAhead": 4, "hourOfDay": 13})
